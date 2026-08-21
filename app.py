from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask import abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave-secreta-vendora"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://testuser:123456@localhost:3306/Vendora'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column("usu_id", db.Integer, primary_key=True)
    nome = db.Column("usu_nome", db.String(256))
    email = db.Column("usu_email", db.String(256))
    senha = db.Column("usu_senha", db.String(256))

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            return redirect(url_for("index"))

        return render_template(
            "login.html",
            erro="E-mail ou senha inválidos."
        )

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# PERFIL DO USUÁRIO

@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():

    usuario = Usuario.query.get(current_user.id)

    if not usuario:
        abort(404)

    endereco = Endereco.query.filter_by(
        usu_id=usuario.id
    ).first()

    if request.method == "POST":

        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")

        senha = request.form.get("senha")

        if senha:
            usuario.senha = generate_password_hash(senha)

        if endereco:

            endereco.rua = request.form.get("rua")
            endereco.numero = request.form.get("numero")
            endereco.bairro = request.form.get("bairro")
            endereco.cidade = request.form.get("cidade")
            endereco.cep = request.form.get("cep")

        else:

            endereco = Endereco(
                request.form.get("rua"),
                request.form.get("numero"),
                request.form.get("bairro"),
                request.form.get("cidade"),
                request.form.get("cep"),
                usuario.id
            )

            db.session.add(endereco)

        db.session.commit()

        return redirect(url_for("perfil"))

    return render_template(
        "perfil.html",
        usuario=usuario,
        endereco=endereco
    )

#Home/Index
@app.route("/")
def index():
    return render_template("index.html")

#Cadastro Usuário
@app.route("/cad/usuario")
def usuario():
    usuarios = Usuario.query.all()
    enderecos = Endereco.query.all()

    return render_template(
        "usuario.html",
        usuarios=usuarios,
        enderecos=enderecos
    )


@app.route("/usuario/criar", methods=["POST"])
def criarusuario():

    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")

    rua = request.form.get("rua")
    numero = request.form.get("numero")
    bairro = request.form.get("bairro")
    cidade = request.form.get("cidade")
    cep = request.form.get("cep")

    senha_hash = generate_password_hash(senha)

    usuario = Usuario(
        nome,
        email,
        senha_hash
    )

    db.session.add(usuario)
    db.session.commit()

    endereco = Endereco(
        rua,
        numero,
        bairro,
        cidade,
        cep,
        usuario.id
    )

    db.session.add(endereco)
    db.session.commit()

    return redirect(url_for("usuario"))

#Editar Usuário
@app.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarusuario(id):
    usuario = Usuario.query.get(id)

    if not usuario:
        abort(404)

    endereco = Endereco.query.filter_by(usu_id=id).first()

    if request.method == "POST":

        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
        usuario.senha = request.form.get("senha")

        if endereco:
            endereco.rua = request.form.get("rua")
            endereco.numero = request.form.get("numero")
            endereco.bairro = request.form.get("bairro")
            endereco.cidade = request.form.get("cidade")
            endereco.cep = request.form.get("cep")

        else:
            endereco = Endereco(
                request.form.get("rua"),
                request.form.get("numero"),
                request.form.get("bairro"),
                request.form.get("cidade"),
                request.form.get("cep"),
                usuario.id
            )

            db.session.add(endereco)

        db.session.commit()

        return redirect(url_for("usuario"))

    return render_template(
        "editarusuario.html",
        usuario=usuario,
        endereco=endereco
    )

#Excluir Usuário
@app.route("/usuario/deletar/<int:id>")
@login_required
def deletarusuario(id):

    usuario = Usuario.query.get(id)

    if usuario:

        endereco = Endereco.query.filter_by(usu_id=id).first()

        if endereco:
            db.session.delete(endereco)

        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for("usuario"))

#Endereço
class Endereco(db.Model):
    __tablename__ = "endereco"

    id = db.Column("end_id", db.Integer, primary_key=True)
    rua = db.Column("end_rua", db.String(256))
    numero = db.Column("end_numero", db.String(20))
    bairro = db.Column("end_bairro", db.String(256))
    cidade = db.Column("end_cidade", db.String(256))
    cep = db.Column("end_cep", db.String(10))

    usu_id = db.Column(
        "usu_id",
        db.Integer,
        db.ForeignKey("usuario.usu_id")
    )

    def __init__(self, rua, numero, bairro, cidade, cep, usu_id):
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.cep = cep
        self.usu_id = usu_id

# CATEGORIA
class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column("cat_id", db.Integer, primary_key=True)
    nome = db.Column("cat_nome", db.String(256))
    descricao = db.Column("cat_descricao", db.String(500))

    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao

@app.route("/cad/categoria")
@login_required
def categoria():

    categorias = Categoria.query.all()

    return render_template(
        "categoria.html",
        categorias=categorias
    )

@app.route("/categoria/criar", methods=["POST"])
@login_required
def criarcategoria():

    nome = request.form.get("nome")
    descricao = request.form.get("descricao")

    categoria = Categoria(
        nome,
        descricao
    )

    db.session.add(categoria)
    db.session.commit()

    return redirect(url_for("categoria"))

@app.route("/categoria/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarcategoria(id):

    categoria = Categoria.query.get(id)

    if not categoria:
        abort(404)

    if request.method == "POST":

        categoria.nome = request.form.get("nome")
        categoria.descricao = request.form.get("descricao")

        db.session.commit()

        return redirect(url_for("categoria"))

    return render_template(
        "editarcategoria.html",
        categoria=categoria
    )       
 
@app.route("/categoria/deletar/<int:id>")
@login_required
def deletarcategoria(id):

    categoria = Categoria.query.get(id)

    if not categoria:
        abort(404)

    if categoria:

        db.session.delete(categoria)
        db.session.commit()

    return redirect(url_for("categoria"))

# ANÚNCIO
class Anuncio(db.Model):
    __tablename__ = "anuncio"

    id = db.Column("anu_id", db.Integer, primary_key=True)
    titulo = db.Column("anu_titulo", db.String(256))
    descricao = db.Column("anu_descricao", db.String(500))
    preco = db.Column("anu_preco", db.Float)
    quantidade = db.Column("anu_quantidade", db.Integer)

    usu_id = db.Column(
        "usu_id",
        db.Integer,
        db.ForeignKey("usuario.usu_id")
    )

    cat_id = db.Column(
        "cat_id",
        db.Integer,
        db.ForeignKey("categoria.cat_id")
    )

    usuario = db.relationship("Usuario")
    categoria = db.relationship("Categoria")

    def __init__(
        self,
        titulo,
        descricao,
        preco,
        quantidade,
        usu_id,
        cat_id
    ):
        self.titulo = titulo
        self.descricao = descricao
        self.preco = preco
        self.quantidade = quantidade
        self.usu_id = usu_id
        self.cat_id = cat_id

@app.route("/cad/anuncio")
@login_required
def anuncio():

    anuncios = Anuncio.query.all()
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()

    return render_template(
        "anuncio.html",
        anuncios=anuncios,
        categorias=categorias,
        usuarios=usuarios
    )

@app.route("/anuncio/criar", methods=["POST"])
@login_required
def criaranuncio():

    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    preco = request.form.get("preco")
    quantidade = request.form.get("quantidade")
    cat_id = request.form.get("cat_id")
    usu_id = request.form.get("usu_id")

    anuncio = Anuncio(
        titulo,
        descricao,
        preco,
        quantidade,
        usu_id,
        cat_id
    )

    db.session.add(anuncio)
    db.session.commit()

    return redirect(url_for("anuncio"))

@app.route("/anuncio/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editaranuncio(id):

    anuncio = Anuncio.query.get(id)

    if not anuncio:
        abort(404)

    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()

    if request.method == "POST":

        anuncio.titulo = request.form.get("titulo")
        anuncio.descricao = request.form.get("descricao")
        anuncio.preco = request.form.get("preco")
        anuncio.quantidade = request.form.get("quantidade")
        anuncio.cat_id = request.form.get("cat_id")
        anuncio.usu_id = request.form.get("usu_id")

        db.session.commit()

        return redirect(url_for("anuncio"))

    return render_template(
        "editaranuncio.html",
        anuncio=anuncio,
        categorias=categorias,
        usuarios=usuarios
    )

@app.route("/anuncio/deletar/<int:id>")
@login_required
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)

    if not anuncio:
        abort(404)

    if anuncio:
        db.session.delete(anuncio)
        db.session.commit()

    return redirect(url_for("anuncio"))

# PERGUNTA
class Pergunta(db.Model):
    __tablename__ = "pergunta"

    id = db.Column("per_id", db.Integer, primary_key=True)
    texto = db.Column("per_texto", db.String(500))

    usu_id = db.Column(
        "usu_id",
        db.Integer,
        db.ForeignKey("usuario.usu_id")
    )

    anu_id = db.Column(
        "anu_id",
        db.Integer,
        db.ForeignKey("anuncio.anu_id")
    )

    usuario = db.relationship("Usuario")
    anuncio = db.relationship("Anuncio")

    def __init__(self, texto, usu_id, anu_id):
        self.texto = texto
        self.usu_id = usu_id
        self.anu_id = anu_id

@app.route("/cad/pergunta")
@login_required
def pergunta():

    perguntas = Pergunta.query.all()
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()

    return render_template(
        "pergunta.html",
        perguntas=perguntas,
        usuarios=usuarios,
        anuncios=anuncios
    )

@app.route("/pergunta/criar", methods=["POST"])
@login_required
def criarpergunta():

    texto = request.form.get("texto")
    usu_id = request.form.get("usu_id")
    anu_id = request.form.get("anu_id")

    pergunta = Pergunta(
        texto,
        usu_id,
        anu_id
    )

    db.session.add(pergunta)
    db.session.commit()

    return redirect(url_for("pergunta"))

@app.route("/pergunta/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarpergunta(id):

    pergunta = Pergunta.query.get(id)

    if not pergunta:
        abort(404)

    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()

    if request.method == "POST":

        pergunta.texto = request.form.get("texto")
        pergunta.usu_id = request.form.get("usu_id")
        pergunta.anu_id = request.form.get("anu_id")

        db.session.commit()

        return redirect(url_for("pergunta"))

    return render_template(
        "editarpergunta.html",
        pergunta=pergunta,
        usuarios=usuarios,
        anuncios=anuncios
    )

@app.route("/pergunta/deletar/<int:id>")
@login_required
def deletarpergunta(id):

    pergunta = Pergunta.query.get(id)

    if not pergunta:
        abort(404)

    if pergunta:

        db.session.delete(pergunta)
        db.session.commit()

    return redirect(url_for("pergunta"))

# RESPOSTA
class Resposta(db.Model):
    __tablename__ = "resposta"

    id = db.Column("res_id", db.Integer, primary_key=True)
    texto = db.Column("res_texto", db.String(500))

    usu_id = db.Column(
        "usu_id",
        db.Integer,
        db.ForeignKey("usuario.usu_id")
    )

    per_id = db.Column(
        "per_id",
        db.Integer,
        db.ForeignKey("pergunta.per_id"),
        unique=True
    )

    usuario = db.relationship("Usuario")
    pergunta = db.relationship("Pergunta")

    def __init__(self, texto, usu_id, per_id):
        self.texto = texto
        self.usu_id = usu_id
        self.per_id = per_id

@app.route("/cad/resposta")
@login_required
def resposta():

    respostas = Resposta.query.all()
    usuarios = Usuario.query.all()
    perguntas = Pergunta.query.all()

    return render_template(
        "resposta.html",
        respostas=respostas,
        usuarios=usuarios,
        perguntas=perguntas
    )

@app.route("/resposta/criar", methods=["POST"])
@login_required
def criarresposta():

    texto = request.form.get("texto")
    usu_id = request.form.get("usu_id")
    per_id = request.form.get("per_id")

    resposta = Resposta(
        texto,
        usu_id,
        per_id
    )

    db.session.add(resposta)
    db.session.commit()

    return redirect(url_for("resposta"))

@app.route("/resposta/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarresposta(id):

    resposta = Resposta.query.get(id)

    if not resposta:
        abort(404)

    usuarios = Usuario.query.all()
    perguntas = Pergunta.query.all()

    if request.method == "POST":

        resposta.texto = request.form.get("texto")
        resposta.usu_id = request.form.get("usu_id")
        resposta.per_id = request.form.get("per_id")

        db.session.commit()

        return redirect(url_for("resposta"))

    return render_template(
        "editarresposta.html",
        resposta=resposta,
        usuarios=usuarios,
        perguntas=perguntas
    )

@app.route("/resposta/deletar/<int:id>")
@login_required
def deletarresposta(id):

    resposta = Resposta.query.get(id)

    if not resposta:
        abort(404)

    if resposta:

        db.session.delete(resposta)
        db.session.commit()

    return redirect(url_for("resposta"))

# COMPRA
class Compra(db.Model):
    __tablename__ = "compra"

    id = db.Column("com_id", db.Integer, primary_key=True)
    quantidade = db.Column("com_quantidade", db.Integer)
    valor = db.Column("com_valor", db.Float)

    usu_id = db.Column(
        "usu_id",
        db.Integer,
        db.ForeignKey("usuario.usu_id")
    )

    anu_id = db.Column(
        "anu_id",
        db.Integer,
        db.ForeignKey("anuncio.anu_id")
    )

    usuario = db.relationship("Usuario")
    anuncio = db.relationship("Anuncio")

    def __init__(self, quantidade, valor, usu_id, anu_id):
        self.quantidade = quantidade
        self.valor = valor
        self.usu_id = usu_id
        self.anu_id = anu_id

@app.route("/cad/compra")
@login_required
def compra():

    compras = Compra.query.all()
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()

    return render_template(
        "compra.html",
        compras=compras,
        usuarios=usuarios,
        anuncios=anuncios
    )

@app.route("/compra/criar", methods=["POST"])
@login_required
def criarcompra():

    quantidade = request.form.get("quantidade")
    valor = request.form.get("valor")
    usu_id = request.form.get("usu_id")
    anu_id = request.form.get("anu_id")

    compra = Compra(
        quantidade,
        valor,
        usu_id,
        anu_id
    )

    db.session.add(compra)
    db.session.commit()

    return redirect(url_for("compra"))

@app.route("/compra/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarcompra(id):

    compra = Compra.query.get(id)

    if not compra:
        abort(404)

    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()

    if request.method == "POST":

        compra.quantidade = request.form.get("quantidade")
        compra.valor = request.form.get("valor")
        compra.usu_id = request.form.get("usu_id")
        compra.anu_id = request.form.get("anu_id")

        db.session.commit()

        return redirect(url_for("compra"))

    return render_template(
        "editarcompra.html",
        compra=compra,
        usuarios=usuarios,
        anuncios=anuncios
    )

@app.route("/compra/deletar/<int:id>")
@login_required
def deletarcompra(id):

    compra = Compra.query.get(id)

    if not compra:
        abort(404)

    if compra:

        db.session.delete(compra)
        db.session.commit()

    return redirect(url_for("compra"))

# FAVORITA
class Favorita(db.Model):
    __tablename__ = "favorita"

    id = db.Column("fav_id", db.Integer, primary_key=True)

    usu_id = db.Column(
        "usu_id",
        db.Integer,
        db.ForeignKey("usuario.usu_id")
    )

    anu_id = db.Column(
        "anu_id",
        db.Integer,
        db.ForeignKey("anuncio.anu_id")
    )

    usuario = db.relationship("Usuario")
    anuncio = db.relationship("Anuncio")

    def __init__(self, usu_id, anu_id):
        self.usu_id = usu_id
        self.anu_id = anu_id

@app.route("/cad/favorita")
@login_required
def favorita():

    favoritas = Favorita.query.all()
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()

    return render_template(
        "favorita.html",
        favoritas=favoritas,
        usuarios=usuarios,
        anuncios=anuncios
    )

@app.route("/favorita/criar", methods=["POST"])
@login_required
def criarfavorita():

    usu_id = request.form.get("usu_id")
    anu_id = request.form.get("anu_id")

    favorita = Favorita(
        usu_id,
        anu_id
    )

    db.session.add(favorita)
    db.session.commit()

    return redirect(url_for("favorita"))

@app.route("/favorita/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editarfavorita(id):

    favorita = Favorita.query.get(id)

    if not favorita:
        abort(404)

    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()

    if request.method == "POST":

        favorita.usu_id = request.form.get("usu_id")
        favorita.anu_id = request.form.get("anu_id")

        db.session.commit()

        return redirect(url_for("favorita"))

    return render_template(
        "editarfavorita.html",
        favorita=favorita,
        usuarios=usuarios,
        anuncios=anuncios
    )

@app.route("/favorita/deletar/<int:id>")
@login_required
def deletarfavorita(id):

    favorita = Favorita.query.get(id)

    if not favorita:
        abort(404)

    if favorita:

        db.session.delete(favorita)
        db.session.commit()

    return redirect(url_for("favorita"))

# RELATÓRIOS

@app.route("/relatorios")
@login_required
def relatorios():

    return render_template("relatorios.html")


@app.route("/relatorios/compras")
@login_required
def relcompras():

    compras = Compra.query.filter_by(
        usu_id=current_user.id
    ).all()

    total_quantidade = sum(
        compra.quantidade for compra in compras
    )

    total_compras = sum(
        compra.valor for compra in compras
    )

    return render_template(
        "relcompras.html",
        compras=compras,
        total_quantidade=total_quantidade,
        total_compras=total_compras
    )


@app.route("/relatorios/vendas")
@login_required
def relvendas():

    vendas = Compra.query.join(
        Anuncio,
        Compra.anu_id == Anuncio.id
    ).filter(
        Anuncio.usu_id == current_user.id
    ).all()

    total_quantidade = sum(
        venda.quantidade for venda in vendas
    )

    total_vendas = sum(
        venda.valor for venda in vendas
    )

    return render_template(
        "relvendas.html",
        vendas=vendas,
        total_quantidade=total_quantidade,
        total_vendas=total_vendas
    )

# Tratamento de erros de página ou requisição

# Tratamento de erro 404 - Página não encontrada 
@app.errorhandler(404) 
def pagina_nao_encontrada(erro): 
    return render_template( "erro.html", 
        descricao="A página que você está procurando não existe." ), 404

# Tratamento de erro 403 - Sem permissão de acesso
@app.errorhandler(403)
def acesso_negado(erro): 
    return render_template( "erro.html", codigo=403, 
        descricao="Você não tem permissão para acessar esta página." ), 403

# Tratamento de erro 405 - Operação não permitida 
@app.errorhandler(405)
def metodo_nao_permitido(erro): 
    return render_template( "erro.html", codigo=405, 
        descricao="A operação solicitada não é permitida nesta página." ), 405


# Tratamento de erro 500 - Erro Interno do servidor
@app.errorhandler(500)
def erro_interno(erro): 
    return render_template( "erro.html", codigo=500, 
        descricao="Ocorreu um erro interno. Tente novamente mais tarde." ), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)