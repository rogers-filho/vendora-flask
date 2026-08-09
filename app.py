from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request


app = Flask(__name__)


# HOME
@app.route("/")
def index():
    return render_template("index.html")


# LOGIN
@app.route("/login")
def login():
    return render_template("login.html")


# CADASTRO
@app.route("/cad/usuario")
def usuario():
    return render_template("usuario.html", titulo="Cadastro de Usuário")


@app.route("/cad/caduser", methods=["POST"])
def caduser():
    return request.form


# ANÚNCIOS
@app.route("/anuncios")
def anuncios():
    return render_template("anuncios.html")


@app.route("/cad/anuncio")
def anuncio():
    return render_template("anuncio.html")


@app.route("/anuncios/pergunta")
def pergunta():
    return render_template("pergunta.html")


@app.route("/anuncios/compra")
def compra():
    print("Anúncio comprado")
    return "Compra realizada com sucesso!"


# MEUS ANÚNCIOS
@app.route("/meus-anuncios")
def meusAnuncios():
    return render_template("meusAnuncios.html")


# FAVORITOS
@app.route("/favoritos")
def favoritos():
    return render_template("favoritos.html")


@app.route("/anuncio/favoritos")
def adicionarFavorito():
    print("Favorito inserido")
    return "Anúncio adicionado aos favoritos!"


# COMPRAS
@app.route("/minhas-compras")
def minhasCompras():
    return render_template("minhasCompras.html")


# CATEGORIAS
@app.route("/config/categoria")
def categoria():
    return render_template("categoria.html")


# RELATÓRIOS
@app.route("/relatorios")
def relatorios():
    return render_template("relatorios.html")


@app.route("/relatorios/vendas")
def relVendas():
    return render_template("relVendas.html")


@app.route("/relatorios/compras")
def relCompras():
    return render_template("relCompras.html")


# MEU PERFIL
@app.route("/perfil")
def perfil():
    return render_template("perfil.html")


@app.route("/perfil/enderecos")
def enderecos():
    return render_template("enderecos.html")


if __name__ == "__main__":
    app.run(debug=True)