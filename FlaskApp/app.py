from flask import Flask, render_template, request, jsonify
import ply.yacc as yacc
import ply.lex as lex
from graphviz import Digraph

app = Flask(__name__)

# Tokens
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'LPAREN',
    'RPAREN',
)

# Reglas de los tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore = ' \t'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_error(t):
    print(f"Token no válido: {t.value[0]}")
    t.lexer.skip(1)

# Analizador léxico
lexer = lex.lex()

# Gramática independiente del contexto
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = ('+', p[1], p[3])

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = ('-', p[1], p[3])

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_mult(p):
    'term : term MULT factor'
    p[0] = ('*', p[1], p[3])

def p_term_div(p):
    'term : term DIV factor'
    p[0] = ('/', p[1], p[3])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

def p_error(p):
    print("Error de sintaxis.")

# Analizador sintáctico
parser = yacc.yacc()

# Función para generar el árbol gráfico
def generate_tree(node, graph=None, parent=None, counter=None):
    if graph is None:
        graph = Digraph()
        counter = [0]

    current_id = f'node{counter[0]}'
    label = str(node[0]) if isinstance(node, tuple) else str(node)
    graph.node(current_id, label)
    counter[0] += 1

    if parent:
        graph.edge(parent, current_id)

    if isinstance(node, tuple):
        for child in node[1:]:
            generate_tree(child, graph, current_id, counter)

    return graph

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.json.get('expression', '')
    try:
        parsed_result = parser.parse(expression)
        result = eval(expression)  # Calcula el resultado numérico
        graph = generate_tree(parsed_result)
        graph.render('static/tree', format='png', cleanup=True)  # Genera el árbol gráfico
        return jsonify({
            'result': result,
            'tree': '/static/tree.png'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
