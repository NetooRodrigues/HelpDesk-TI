from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def criar_banco():
    conexao = sqlite3.connect("helpdesk.db")

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            status TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


@app.route("/")
def inicio():
    conexao = sqlite3.connect("helpdesk.db")
    conexao.row_factory = sqlite3.Row

    chamados = conexao.execute("""
        SELECT * FROM chamados
        ORDER BY id DESC
    """).fetchall()

    total = conexao.execute("""
        SELECT COUNT(*) FROM chamados
    """).fetchone()[0]

    abertos = conexao.execute("""
        SELECT COUNT(*) FROM chamados
        WHERE status = 'Aberto'
    """).fetchone()[0]

    resolvidos = conexao.execute("""
        SELECT COUNT(*) FROM chamados
        WHERE status = 'Resolvido'
    """).fetchone()[0]

    alta = conexao.execute("""
        SELECT COUNT(*) FROM chamados
        WHERE prioridade = 'Alta'
    """).fetchone()[0]

    conexao.close()

    return render_template(
        "index.html",
        chamados=chamados,
        total=total,
        abertos=abertos,
        resolvidos=resolvidos,
        alta=alta
    )


@app.route("/criar", methods=["POST"])
def criar():
    titulo = request.form["titulo"]
    descricao = request.form["descricao"]
    prioridade = request.form["prioridade"]
    data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M")
    conexao = sqlite3.connect("helpdesk.db")


    conexao.execute("""
        INSERT INTO chamados (titulo, descricao, prioridade, status, data_criacao)
        VALUES (?, ?, ?, ?, ?)
    """, (titulo, descricao, prioridade, "Aberto", data_criacao))

    conexao.commit()
    conexao.close()

    return redirect("/")

@app.route("/chamado/<int:id>")
def detalhes(id):
    conexao = sqlite3.connect("helpdesk.db")
    conexao.row_factory = sqlite3.Row

    chamado = conexao.execute("""
        SELECT * FROM chamados
        WHERE id = ?
    """, (id,)).fetchone()

    conexao.close()

    return render_template("detalhes.html", chamado=chamado)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexao = sqlite3.connect("helpdesk.db")
    conexao.row_factory = sqlite3.Row

    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        prioridade = request.form["prioridade"]

        conexao.execute("""
            UPDATE chamados
            SET titulo = ?, descricao = ?, prioridade = ?
            WHERE id = ?
        """, (titulo, descricao, prioridade, id))

        conexao.commit()
        conexao.close()

        return redirect(f"/chamado/{id}")

    chamado = conexao.execute("""
        SELECT * FROM chamados
        WHERE id = ?
    """, (id,)).fetchone()

    conexao.close()

    return render_template("editar.html", chamado=chamado)

@app.route("/resolver/<int:id>")
def resolver(id):
    conexao = sqlite3.connect("helpdesk.db")

    conexao.execute("""
        UPDATE chamados
        SET status = ?
        WHERE id = ?
    """, ("Resolvido", id))

    conexao.commit()
    conexao.close()

    return redirect("/")

@app.route("/excluir/<int:id>")
def excluir(id):
    conexao = sqlite3.connect("helpdesk.db")

    conexao.execute("""
        DELETE FROM chamados
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect("/")

if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)