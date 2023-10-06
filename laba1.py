import math
import re
from traceback import format_exc


def _eval_log(expression):
    """calculate log expr and validate params of log"""
    try:
        func_expr = re.search(r"log\((.*?)\)", expression)
        if func_expr:
            args = func_expr.group(1).split(",")
            print("Args of log: ", args)
            try:
                float(args[1])
            except ValueError:
                args[1] = eval(args[1])
            try:
                float(args[0])
            except ValueError:
                args[0] = eval(args[0])
            if float(args[1]) <= 0 or float(args[0]) <= 0 or float(args[0]) == 1:
                raise Exception("Некорректные аргументы функции log")
            res = math.log(float(args[1]), float(args[0]))
            return res
    except Exception as ex:
        print(ex)
        # print(format_exc())
        # exit()


def find(str, ch):
    res = []
    for i, ltr in enumerate(str):
        if ltr == ch:
            res.append(i)
    return res


def find_end(str):
    return str.index(")")


def eval_log(expression):
    """return expr with calculating log"""
    len_index = find(expression, "l")
    if len(len_index) > 1:
        for i in len_index[-1:]:
            res_log = _eval_log(expression[i:])
            end_index = find_end(expression[i:])
            exp = expression[:i] + str(res_log) + expression[i:][end_index + 1 :]
            return exp
    else:
        i = len_index[0]
        res_log = _eval_log(expression)
        end_index = find_end(expression[i:])
        exp = expression[:i] + str(res_log) + expression[i:][end_index + 1 :]
        return exp


def get_exp_without_minus(expression):
    """find minuses in expression and replace them
    return count of minuses in expression and expression without minuses"""
    if re.search(r"\W\(-", expression):
        count_minus = expression.count("(-")
        expression = expression.replace("(-", "(")
        return count_minus, expression
    return 0, expression


def validate_expr(expr):
    if expr[-1] in "+-/*":
        raise Exception("Некорректное выражение. Слишком много операторов")
    if re.search(r"([,.+\-*/])\1", expr):
        raise Exception("Встречаются повторяющиеся символы")
    if re.search(r"\d*\.\d*\.", expr):
        raise Exception(
            "Некорректное значение числа с плавающей точкой, удалите лишние точки"
        )


def calculate(expression):
    """del any spaces in expr
    convert expr to expr without minuses
    get operands and operators of expr
    """
    try:
        validate_expr(expression)

        # Удаляем все пробелы из выражения
        expression = expression.replace(" ", "")

        while "log(" in expression:
            expression = eval_log(expression)
            print("Result log: ", expression)

        operands = []
        operators = []

        # приоритет операторов
        priority = {"+": 1, "-": 1, "*": 2, "/": 2}

        index = 0
        while index < len(expression):
            char = expression[index]
            if char == ".":
                ind_ = index
                number_ = ""
                while index < len(expression):
                    # expression[index+1].isdigit()
                    if index == ind_:
                        number_ += f"0{expression[index]}"
                    elif expression[index].isdigit():
                        number_ += expression[index]
                    else:
                        break
                    index += 1
                operands.append(float(number_))

                if len(operands) == 1 and operators and operators[-1] == "-":
                    operands[-1] = operands[-1] * (-1)
                    operators.pop()
                if (
                    len(operators) > 1
                    and operators[-2] == "("
                    and operators[-1] == "-"
                    and len(operators) > 2
                ): 
                    operands[-1] = operands[-1] * (-1)
                    operators.pop()
                continue

            elif char.isdigit():
                # Если символ - цифра, извлекаем число из выражения и добавляем в список операндов
                number = ""
                while index < len(expression) and (
                    expression[index].isdigit() or expression[index] == "."
                ):
                    number += expression[index]
                    index += 1
                operands.append(float(number))
                if len(operands) == 1 and operators and operators[-1] == "-":
                    operands[-1] = operands[-1] * (-1)
                    operators.pop()
                if (
                    len(operators) > 1
                    and operators[-2] == "("
                    and operators[-1] == "-"
                    and len(operators) > 2
                ):  
                    operands[-1] = operands[-1] * (-1)
                    operators.pop()
                continue
            elif operators and char == "-" and operators[-1] == "(":
                operators.append(char)
            elif char in "+-*/^":
                # Если символ - оператор, проверяем приоритет и добавляем операторы в список
                while (
                    operators
                    and operators[-1] != "("
                    and priority[char] <= priority[operators[-1]]
                ):
                    operands.append(operators.pop())
                operators.append(char)

            elif char == "(":
                # Если символ - "(", просто добавляем его в список операторов
                operators.append(char)

            elif char == ")":
                # Если символ - ")", перемещаем операторы из списка в список операндов,
                # пока не достигнем соответствующей "("
                while operators and operators[-1] != "(":
                    operands.append(operators.pop())
                    if operands[-1] == "-" and not isinstance(operands[-1], str):
                        operands[-2] = operands[-2] * (-1)
                        operands.pop()

                if operators and operators[-1] == "(":
                    operators.pop()
            else:
                raise Exception("Некорректное выражение. В выражении содержатся недопустимые символы")
            index += 1

        # Добавляем оставшиеся операторы в список операндов
        while operators:
            operands.append(operators.pop())

        # Вычисляем результат, проходя по операндам и выполняя соответствующие операции
        stack = []
        i = 0
        for ind, token in enumerate(operands):
            if isinstance(token, str):
                right_operand = stack.pop()
                try:
                    left_operand = stack.pop()
                except Exception:
                    if token == "-":
                        stack.append(right_operand * (-1))
                        continue
                   
                    raise Exception
                

                result = perform_operation(left_operand, right_operand, token)
                stack.append(result)
            else:
                stack.append(token)

        return stack[0]
    except (IndexError, TypeError) as ex:
        print("Некорректное выражение")
        
    except Exception as ex:
        print("Некорректное выражение")
        print(ex)


def perform_operation(left_operand, right_operand, operator):
    try:
        if operator == "+":
            return left_operand + right_operand
        elif operator == "-":
            return left_operand - right_operand
        elif operator == "*":
            return left_operand * right_operand
        elif operator == "/":
            return left_operand / right_operand
        elif operator == "^":
            return left_operand**right_operand
    except ZeroDivisionError as ex:
        print(f"ZeroDivisionError: {ex}")


def main():
    while True:
        expression = input("Введите выражение: ")
        result = calculate(expression)
        print(f"Результат: {result}")


if __name__ == "__main__":
    main()
