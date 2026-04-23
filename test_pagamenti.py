import pytest
from unittest.mock import patch
from contextlib import nullcontext
from pagamenti import elabora_pagamento
from pagamenti import autorizza_transazione

@pytest.mark.parametrize('key, metodo, saldo, importo, expected, result', [
    #SAD PATHS
    (None, 'carta', 100, -20, pytest.raises(ValueError, match="L'importo deve essere maggiore di zero."), None),
    (None, 'alipay', 100, 10, pytest.raises(ValueError, match="Metodo di pagamento non supportato."), None),
    (None, 'crypto', 100, 10, pytest.raises(ValueError, match="L'importo minimo per le crypto è 100"), None),
    (None, 'carta', 20, 70, pytest.raises(ValueError, match="Fondi insufficienti per completare la transazione."), None),

    #HAPPY PATHS
    (False, 'carta', 100, 10, nullcontext(), "Transazione rifiutata dalla banca."),
    (True, 'carta', 2000, 1100, nullcontext(), "Pagamento completato. Richiesta verifica anti-riciclaggio."),
    (True, 'carta', 100, 10, nullcontext(), "Pagamento completato con successo.")
])
@patch('pagamenti.autorizza_transazione')
def test_elab_pagamento(auth, key, metodo, saldo, importo, expected, result):
    auth.return_value = key
    with expected:
        assert elabora_pagamento(metodo, saldo, importo) == result
    assert isinstance(autorizza_transazione(), bool)
    #auth.random.choice.assert_choice_called_once_with([True, False])