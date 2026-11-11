import pytest

import app as portal


@pytest.fixture
def client():
    portal.app.config.update(TESTING=True)
    portal.reiniciar_demo()
    with portal.app.test_client() as c:
        yield c


def entrar(client, perfil, idioma=None):
    if idioma:
        client.get(f"/idioma/{idioma}")
    return client.post("/login", data={"perfil": perfil})
