"""
Clase MathMethods con implementación del método de bisección
"""

import sympy as sp
import numpy as np
from typing import List, Dict, Tuple, Optional
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
import re


class MathMethods:
    """Clase para almacenar y manejar una ecuación matemática en formato string"""

    def __init__(self):
        self.equation_text = ""

    def set_equation(self, equation: str):
        """Establece la ecuación a resolver"""
        self.equation_text = equation

    def get_equation(self) -> str:
        """Retorna la ecuación actual"""
        return self.equation_text

    def get_equation_for_plot(self) -> str:
        """
        Retorna la ecuación en formato compatible con PyQtGraph.
        Convierte notación matemática a Python.
        """
        ecuacion = self.equation_text

        if not ecuacion:
            return ""

        # Reemplazar ^ por **
        ecuacion = ecuacion.replace("^", "**")

        # Agregar * entre número y x (ej: 2x -> 2*x)
        ecuacion = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", ecuacion)

        # Agregar * entre ) y letra o entre letra y (
        ecuacion = re.sub(r"\)([a-zA-Z])", r")*\1", ecuacion)
        ecuacion = re.sub(r"([a-zA-Z])\(", r"\1*(", ecuacion)

        return ecuacion

    @property
    def equation(self):
        """Property para acceder a la ecuación"""
        return self.equation_text

    @equation.setter
    def equation(self, value):
        """Setter para la ecuación"""
        self.equation_text = value

    def bisection_method(
        self, a: float, b: float, tolerance: float = 1e-6, max_iterations: int = 100
    ) -> Dict:
        """
        Implementa el método de bisección para encontrar raíces de una ecuación.
        Devuelve los datos de todas las iteraciones.

        Args:
            a (float): Límite inferior del intervalo
            b (float): Límite superior del intervalo
            tolerance (float): Tolerancia para la convergencia
            max_iterations (int): Número máximo de iteraciones

        Returns:
            Dict: Diccionario con los resultados del método y los datos de las iteraciones.
        """
        iterations_data = []
        try:
            # Parsear la ecuación usando sympy
            x = sp.Symbol("x")
            equation_processed = self._process_equation_for_sympy(self.equation_text)
            expr = sp.sympify(equation_processed)
            f = sp.lambdify(x, expr, "numpy")

            # Verificar que f(a) y f(b) tienen signos opuestos
            fa = f(a)
            fb = f(b)

            if fa * fb > 0:
                return {
                    "success": False,
                    "error": f"f({a}) = {fa:.6f} y f({b}) = {fb:.6f} tienen el mismo signo. No se puede aplicar bisección.",
                    "iterations": 0,
                    "root": None,
                    "final_error": 0.0,
                    "iterations_data": iterations_data,
                }

            # Algoritmo de bisección
            iteration = 0
            c = a
            error = abs(b-a)

            while iteration < max_iterations:
                iteration += 1
                
                c_prev = c
                c = (a + b) / 2
                fc = f(c)

                if iteration > 1:
                    error = abs(c - c_prev)
                else:
                    error = abs(b - a)

                iteration_data = {
                    "iteration": iteration,
                    "a": a,
                    "b": b,
                    "c": c,
                    "f_a": f(a),
                    "f_b": f(b),
                    "f_c": fc,
                    "error": error,
                }
                iterations_data.append(iteration_data)

                if abs(fc) < tolerance or error < tolerance:
                    return {
                        "success": True,
                        "root": c,
                        "iterations": iteration,
                        "final_error": error,
                        "function_value": fc,
                        "message": f"Raíz encontrada en x = {c:.8f} después de {iteration} iteraciones",
                        "iterations_data": iterations_data,
                    }

                if f(a) * fc < 0:
                    b = c
                else:
                    a = c

            return {
                "success": False,
                "error": f"No se alcanzó la convergencia después de {max_iterations} iteraciones",
                "iterations": max_iterations,
                "root": c,
                "final_error": error,
                "iterations_data": iterations_data,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error en el cálculo: {str(e)}",
                "iterations": 0,
                "root": None,
                "final_error": 0.0,
                "iterations_data": iterations_data,
            }

    def _process_equation_for_sympy(self, equation: str) -> str:
        """
        Procesa la ecuación para que sea compatible con sympy.
        Convierte notaciones comunes a formato sympy.
        """
        processed = equation.strip()

        if "=" in processed:
            processed = processed.split("=")[0].strip()

        replacements = {
            "^": "**",
            "sen": "sin",
            "cos": "cos",
            "tan": "tan",
            "ln": "log",
            "log": "log",
            "sqrt": "sqrt",
            "e^": "exp",
        }

        processed = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", processed)
        processed = re.sub(r"([a-zA-Z])\(", r"\1*(", processed)

        for old, new in replacements.items():
            processed = processed.replace(old, new)

        return processed

    def populate_table_rows(self, table_widget, iterations_data):
        """
        Agrega filas a la tabla de la interfaz con los datos de las iteraciones.
        No limpia la tabla, simplemente añade las nuevas filas al final.
        """
        if not iterations_data:
            return

        current_row_count = table_widget.rowCount()
        table_widget.setRowCount(current_row_count + len(iterations_data))

        for i, data in enumerate(iterations_data):
            row_index = current_row_count + i
            table_widget.setItem(row_index, 0, self._create_table_item(str(data["iteration"])))
            table_widget.setItem(row_index, 1, self._create_table_item(f"{data['a']:.6f}"))
            table_widget.setItem(row_index, 2, self._create_table_item(f"{data['b']:.6f}"))
            table_widget.setItem(row_index, 3, self._create_table_item(f"{data['c']:.6f}"))
            table_widget.setItem(row_index, 4, self._create_table_item(f"{data['f_a']:.6f}"))
            table_widget.setItem(row_index, 5, self._create_table_item(f"{data['f_b']:.6f}"))
            table_widget.setItem(row_index, 6, self._create_table_item(f"{data['f_c']:.6f}"))
            table_widget.setItem(row_index, 7, self._create_table_item(f"{data['error']:.6f}"))

        table_widget.resizeColumnsToContents()

    def _create_table_item(self, text: str):
        """
        Crea un item de tabla de Qt con el texto dado.
        """
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def find_all_suitable_intervals(
        self, start: float = -10, end: float = 10, step: float = 0.5
    ) -> List[Tuple[float, float]]:
        """
        Busca automáticamente todos los intervalos adecuados para aplicar bisección.
        Retorna una lista de tuplas (a, b).
        """
        try:
            x = sp.Symbol("x")
            equation_processed = self._process_equation_for_sympy(self.equation_text)
            expr = sp.sympify(equation_processed)
            f = sp.lambdify(x, expr, "numpy")

            intervals = []
            current = start
            while current < end - step:
                try:
                    fa = f(current)
                    fb = f(current + step)

                    if np.sign(fa) != np.sign(fb):
                        intervals.append((current, current + step))

                except (ZeroDivisionError, ValueError, OverflowError):
                    pass
                
                current += step

            return intervals

        except Exception as e:
            print(f"Error buscando intervalos: {e}")
            return []

    def clear_iterations(self):
        """Limpia los datos de iteraciones almacenados"""
        pass

    def get_function_value_at(self, x_value: float) -> float:
        """
        Evalúa la función en un punto específico.
        """
        try:
            x = sp.Symbol("x")
            equation_processed = self._process_equation_for_sympy(self.equation_text)
            expr = sp.sympify(equation_processed)
            f = sp.lambdify(x, expr, "numpy")
            return f(x_value)
        except Exception as e:
            print(f"Error evaluando función en x={x_value}: {e}")
            return float("nan")

    def validate_equation(self) -> Dict:
        """
        Valida que la ecuación sea sintácticamente correcta.
        """
        try:
            if not self.equation_text.strip():
                return {"valid": False, "error": "La ecuación está vacía"}

            x = sp.Symbol("x")
            equation_processed = self._process_equation_for_sympy(self.equation_text)
            expr = sp.sympify(equation_processed)

            f = sp.lambdify(x, expr, "numpy")
            test_value = f(1.0)

            return {
                "valid": True,
                "processed_equation": equation_processed,
                "sympy_expression": str(expr),
            }

        except Exception as e:
            return {"valid": False, "error": f"Error en la ecuación: {str(e)}"}

    def get_summary_statistics(self) -> Dict:
        """
        Retorna estadísticas resumen de la última ejecución de bisección.
        Esta función ya no es necesaria, la lógica se mueve al controlador.
        """
        return {}
    
    def newton_raphson_method(
        self, x0: float, tolerance: float = 1e-6, max_iterations: int = 100
    ) -> Dict:
        """
        Implementa el método de Newton-Raphson para encontrar raíces de una ecuación.
        
        Args:
            x0 (float): Valor inicial
            tolerance (float): Tolerancia para la convergencia
            max_iterations (int): Número máximo de iteraciones
        
        Returns:
            Dict: Diccionario con los resultados del método y los datos de las iteraciones.
        """
        iterations_data = []
        try:
            # Parsear la ecuación usando sympy
            x = sp.Symbol("x")
            equation_processed = self._process_equation_for_sympy(self.equation_text)
            expr = sp.sympify(equation_processed)
            
            # Calcular la derivada
            expr_prime = sp.diff(expr, x)
            
            # Crear funciones lambda
            f = sp.lambdify(x, expr, "numpy")
            f_prime = sp.lambdify(x, expr_prime, "numpy")
            
            # Algoritmo de Newton-Raphson
            iteration = 0
            x_current = x0
            error = float('inf')
            
            while iteration < max_iterations:
                iteration += 1
                
                fx = f(x_current)
                fpx = f_prime(x_current)
                
                # Verificar si la derivada es cero
                if abs(fpx) < 1e-12:
                    return {
                        "success": False,
                        "error": f"La derivada es cero en x = {x_current:.6f}. No se puede continuar.",
                        "iterations": iteration,
                        "root": None,
                        "final_error": error,
                        "iterations_data": iterations_data,
                    }
                
                # Calcular siguiente valor
                x_next = x_current - fx / fpx
                error = abs(x_next - x_current)
                
                iteration_data = {
                    "iteration": iteration,
                    "x": x_current,
                    "f_x": fx,
                    "f_prime_x": fpx,
                    "x_next": x_next,
                    "error": error,
                }
                iterations_data.append(iteration_data)
                
                # Verificar convergencia
                if abs(fx) < tolerance or error < tolerance:
                    return {
                        "success": True,
                        "root": x_next,
                        "iterations": iteration,
                        "final_error": error,
                        "function_value": f(x_next),
                        "message": f"Raíz encontrada en x = {x_next:.8f} después de {iteration} iteraciones",
                        "iterations_data": iterations_data,
                    }
                
                x_current = x_next
            
            return {
                "success": False,
                "error": f"No se alcanzó la convergencia después de {max_iterations} iteraciones",
                "iterations": max_iterations,
                "root": x_current,
                "final_error": error,
                "iterations_data": iterations_data,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en el cálculo: {str(e)}",
                "iterations": 0,
                "root": None,
                "final_error": 0.0,
                "iterations_data": iterations_data,
            }


    def populate_table_newton(self, table_widget, iterations_data):
        """
        Agrega filas a la tabla de la interfaz con los datos de Newton-Raphson.
        No limpia la tabla, simplemente añade las nuevas filas al final.
        """
        if not iterations_data:
            return
        
        current_row_count = table_widget.rowCount()
        table_widget.setRowCount(current_row_count + len(iterations_data))
        
        for i, data in enumerate(iterations_data):
            row_index = current_row_count + i
            table_widget.setItem(row_index, 0, self._create_table_item(str(data["iteration"])))
            table_widget.setItem(row_index, 1, self._create_table_item(f"{data['x']:.6f}"))
            table_widget.setItem(row_index, 2, self._create_table_item(f"{data['f_x']:.6f}"))
            table_widget.setItem(row_index, 3, self._create_table_item(f"{data['f_prime_x']:.6f}"))
            table_widget.setItem(row_index, 4, self._create_table_item(f"{data['x_next']:.6f}"))
            table_widget.setItem(row_index, 5, self._create_table_item(f"{data['error']:.6f}"))
        
        table_widget.resizeColumnsToContents()


    def find_suitable_initial_values(
        self, start: float = -10, end: float = 10, step: float = 1.0, num_values: int = 5
    ) -> List[float]:
        """
        Busca valores iniciales adecuados para Newton-Raphson.
        Busca puntos donde f(x) está cerca de cero o donde cambia de signo.
        
        Args:
            start: Inicio del rango de búsqueda
            end: Fin del rango de búsqueda
            step: Paso de búsqueda
            num_values: Número máximo de valores a retornar
        
        Returns:
            Lista de valores iniciales prometedores
        """
        try:
            x = sp.Symbol("x")
            equation_processed = self._process_equation_for_sympy(self.equation_text)
            expr = sp.sympify(equation_processed)
            f = sp.lambdify(x, expr, "numpy")
            
            candidates = []
            current = start
            
            while current < end:
                try:
                    fx = f(current)
                    # Buscar puntos donde f(x) está cerca de cero
                    if abs(fx) < 10:  # Umbral ajustable
                        candidates.append((current, abs(fx)))
                    
                    # Buscar cambios de signo
                    if current + step < end:
                        fx_next = f(current + step)
                        if np.sign(fx) != np.sign(fx_next):
                            mid = (current + current + step) / 2
                            candidates.append((mid, abs(f(mid))))
                            
                except (ZeroDivisionError, ValueError, OverflowError):
                    pass
                
                current += step
            
            # Ordenar por cercanía a cero y retornar los mejores
            candidates.sort(key=lambda x: x[1])
            return [x[0] for x in candidates[:num_values]]
            
        except Exception as e:
            print(f"Error buscando valores iniciales: {e}")
            return [0.0]  # Valor por defecto