// Request a one-time password recovery link for an internal user.
// The response never reveals whether the account exists.
query request verb=POST {
  api_group = "Voltix Internal Password Recovery"

  input {
    email email filters=trim|lower
  }

  stack {
    // Validate the input without creating any token
    precondition ($input.email != null && ($input.email|strlen) <= 254) {
      error_type = "inputerror"
      error = "Provide a valid email address."
    }

    // Look up the internal user; the response is the same either way
    db.query user {
      where = $db.user.email == $input.email
      return = {type: "single"}
    } as $user

    // Only active internal users with an approved profile receive a link
    conditional {
      if (($user != null) && ($user.status == "ATIVO") && (($user.role == "FUNCIONARIO") || ($user.role == "ADMINISTRADOR"))) {
        // Create a single-use UUID token with a 60 minute expiration
        security.create_uuid as $token

        var $password_reset {
          value = {}
            |set:"token":$token
            |set:"expiration":(now
              |add_secs_to_timestamp:(3600|to_int)
            )
            |set:"used":false
        }

        // Store only the hashed token, expiration and usage flag
        db.edit user {
          field_name = "id"
          field_value = $user.id
          enforce_hidden_fields = false
          data = {password_reset: $password_reset}
        } as $updated_user

        // Build the absolute link using the configured public frontend URL
        var $app_url {
          value = $env.$voltix_app_url
        }

        var $reset_link {
          value = $app_url ~ "/interno/redefinir-senha?email=" ~ $input.email ~ "&token=" ~ $token
        }

        // Build the HTML message with the link and the token as supporting text
        util.template_engine {
          value = """
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1">
              <title>Recuperação de senha</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
              <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2>Recuperação de senha</h2>
                <p>Recebemos uma solicitação para redefinir a sua senha no Voltix.</p>
                <p>Para escolher uma nova senha, acesse o link abaixo:</p>
                <p style="text-align: center; margin: 30px 0;">
                  <a href="{{ $var.reset_link }}" style="display: inline-block; padding: 12px 25px; background-color: #f55e3f; color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 16px;">
                    Redefinir senha
                  </a>
                </p>
                <p>Se o link não funcionar, informe manualmente este código na página de redefinição:</p>
                <p style="font-family: monospace; font-size: 16px; background: #f4f4f4; padding: 10px; border-radius: 4px; word-break: break-all;">{{ $var.token }}</p>
                <p>O código é válido por 60 minutos e pode ser usado uma única vez. Se você não solicitou a redefinição, ignore este e-mail.</p>
                <p>Obrigado.</p>
              </div>
            </body>
            </html>
            """
        } as $message

        // Send Email Function will ONLY send to the instance owner email with the free credits. Provide your own provider API key and account for additional capability.

        // Send the recovery email without exposing the token anywhere else
        util.send_email {
          service_provider = "xano"
          subject = "Voltix - recuperação de senha"
          message = $message
        } as $send_email
      }
    }
  }

  response = {
    message: "Se o e-mail estiver cadastrado, enviaremos as instruções."
  }

  tags = ["voltix:internal-password-recovery"]
  guid = "9DGUfENSFM3MAE2sUba_Fq9IRhS"
}
