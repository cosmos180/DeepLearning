package sealed

sealed class Expr
data class Const(val number: Double) : Expr()
data class Sum(val e1: Expr, val e2: Expr): Expr()
object NotNumber: Expr()

class SealedClass {
    companion object {
        fun eval(expr: Expr): Double = when(expr) {
            is Const -> expr.number
            is Sum -> eval(expr.e1) + eval(expr.e2)
            NotNumber -> Double.NaN
        }
    }
}