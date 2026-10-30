import unittest

from voltix.voltix import State


class InternalWorkspaceNavigationTests(unittest.TestCase):
    def state(self, role="FUNCIONARIO"):
        state = State(_reflex_internal_init=True)
        state._auth_token = "isolated-test-token"
        state.is_authenticated = True
        state.session_status = "success"
        state.user_status = "ATIVO"
        state.user_role = role
        return state

    def test_employee_cannot_select_administrative_or_unknown_section(self):
        state = self.state()
        for section in ["produtos", "catalogo", "importacao", "unknown", None, []]:
            State.select_internal_section.fn(state, section)
            self.assertEqual(state.internal_section, "clientes")

    def test_administrator_selects_only_known_sections(self):
        state = self.state("ADMINISTRADOR")
        for section in ["produtos", "catalogo", "importacao", "clientes"]:
            State.select_internal_section.fn(state, section)
            self.assertEqual(state.internal_section, section)
        State.select_internal_section.fn(state, "unknown")
        self.assertEqual(state.internal_section, "clientes")

    def test_session_guards_block_selection_and_clearing_resets_it(self):
        for field, value in [("_auth_token", ""), ("user_status", "INATIVO"),
                             ("session_status", "error"), ("user_role", "CLIENTE")]:
            state = self.state("ADMINISTRADOR")
            setattr(state, field, value)
            State.select_internal_section.fn(state, "produtos")
            self.assertEqual(state.internal_section, "clientes")
        state = self.state("ADMINISTRADOR")
        State.select_internal_section.fn(state, "importacao")
        state._clear_authentication_state("", session_status="idle")
        self.assertEqual(state.internal_section, "clientes")
        self.assertFalse(state.is_authenticated)
