class MathEngine:
    def _get_sympy(self):
        try:
            import sympy
            from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
            return sympy, parse_expr, standard_transformations, implicit_multiplication_application
        except ImportError:
            return None, None, None, None
    def process(self, request: str, health_check: bool = False) -> dict:
        """Contrato unificado: Resuelve problemas usando SymPy (Lazy Load)."""
        if health_check:
            sympy, _, _, _ = self._get_sympy()
            return {"status": "success" if sympy else "error", "message": "MathEngine ready."}

        sympy, parse_expr, standard_transformations, implicit_multiplication_application = self._get_sympy()
        if not sympy:
            return {
                "status": "error",
                "message": "SymPy no instalado.",
                "instructions_for_llm": "Resuelve matemáticamente usando tu propio razonamiento."
            }


        expression_str = self._extract_expression(request)
        try:
            transformations = (standard_transformations + (implicit_multiplication_application,))
            expr = parse_expr(expression_str, transformations=transformations)
            steps = []
            solution = None
            
            if "x" in expression_str and "=" in expression_str:
                parts = expression_str.split("=")
                lhs = parse_expr(parts[0], transformations=transformations)
                rhs = parse_expr(parts[1], transformations=transformations)
                eq = sympy.Eq(lhs, rhs)
                sol = sympy.solve(eq)
                solution = str(sol)
                steps.append(f"1. Ecuación: {lhs} = {rhs}")
                steps.append(f"2. Solución: {solution}")
            else:
                sol = expr.evalf()
                solution = str(sol)
                steps.append(f"1. Evaluar: {expr}")
                steps.append(f"2. Resultado: {solution}")

            return {
                "status": "success",
                "detected_expression": expression_str,
                "solution": solution,
                "steps": steps,
                "instructions_for_llm": f"La solución a {expression_str} es {solution}."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_expression(self, text: str) -> str:
        # Very naive extraction: remove common words, keep math chars
        # This is a placeholder for a better extractor
        
        ignored = ["calcula", "cuánto", "es", "la", "de", "el", "resuelve", "x", "y"] 
        # Wait, x and y are variables.
        text = text.lower()
        cleaned = text.replace("calcula", "").replace("resuelve", "").replace("cuanto es", "")
        # Remove text, keep typical math chars
        # Allow: 0-9, x, y, z, +, -, *, /, ^, (, ), =, ., sin, cos, tan, log, sqrt, diff, int
        
        # Taking a shortcut: just return the part that looks most like an equation?
        # For v2.4 simplicity, let's assume the user input contains the expression clearly.
        # Let's clean up 'calculate' etc.
        
        return cleaned.strip()
