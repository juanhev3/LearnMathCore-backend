from flask import Flask, request, jsonify
from sympy import Symbol, sympify, integrate, diff, simplify, latex
from sympy.parsing.sympy_parser import parse_expr
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        expr_text = data.get("expression", "").strip()
        x = Symbol('x')

        # Handle integrate
        if expr_text.startswith("integrate(") and expr_text.endswith(")"):
            inner = expr_text[len("integrate("):-1]
            parts = [s.strip() for s in inner.split(",")]
            if len(parts) != 2:
                raise ValueError("integrate() must have two arguments.")
            expr = parse_expr(parts[0])
            var = Symbol(parts[1])
            result = integrate(expr, var)
            rendered_input = f"\\int {latex(expr)} \\, d{latex(var)}"

        # Handle diff
        elif expr_text.startswith("diff(") and expr_text.endswith(")"):
            inner = expr_text[len("diff("):-1]
            parts = [s.strip() for s in inner.split(",")]
            if len(parts) != 2:
                raise ValueError("diff() must have two arguments.")
            expr = parse_expr(parts[0])
            var = Symbol(parts[1])
            result = diff(expr, var)
            rendered_input = f"\\frac{{d}}{{d{latex(var)}}}\\left({latex(expr)}\\right)"

        # Handle d/dx shortcut
        elif expr_text.startswith("d/dx(") and expr_text.endswith(")"):
            inner = expr_text[len("d/dx("):-1]
            expr = parse_expr(inner)
            result = diff(expr, x)
            rendered_input = f"\\frac{{d}}{{dx}}\\left({latex(expr)}\\right)"

        else:
            # Simplify normal expressions
            expr = parse_expr(expr_text)
            result = simplify(expr)
            rendered_input = latex(expr)

        return jsonify({
            "input": f"${rendered_input}$",
            "output": f"$= {latex(result)}$"
        })

    except Exception as e:
        return jsonify({
            "input": f"${expr_text}$",
            "output": f"<span style='color:red;'>Error: {str(e)}</span>"
        }), 400

if __name__ == "__main__":
    app.run(port=5000)
