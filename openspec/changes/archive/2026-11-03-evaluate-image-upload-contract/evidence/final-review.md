# Revisão final — contrato do upload de imagem

Data: 04/11/2026.

- Revisado o handler Reflex, a definição XanoScript local, a evidência histórica HTTP 403 e o trecho do endpoint publicado fornecido pelo usuário.
- O painel envia exatamente o campo `image_file`; a guarda do endpoint publicado exige Administrador ativo e produto existente, e o armazenamento está privado.
- O endpoint publicado declara `file? image_file` opcional, mas usa o arquivo e seu `.name` sem verificar presença. O XanoScript local declara o arquivo obrigatório. Não foi testada chamada sem arquivo.
- O HTTP 403 histórico foi atribuído a uma limitação do `storage.create_image` no plano Free, separada da opcionalidade do campo. Upload atual continua sem validação operacional.
- O pull do workspace inteiro foi rejeitado pela revisão automática por trazer metadados privados fora do escopo; a alternativa scoped veio do código que o usuário copiou. Não houve contorno, upload, POST, publicação ou alteração de código/Xano.
- Entrega documental concluída, sem alteração de specs (`skip_specs: true`). OpenSpec estrito e diff documental revisados; nenhuma suíte funcional foi executada.
- Próximo passo funcional, se desejado, é uma change OpenSpec independente para tornar o input obrigatório/validar arquivo e resolver a disponibilidade do armazenamento em ambiente autorizado que ofereça `storage.create_image`. Esta change não implementa a correção nem declara o serviço operacional.
