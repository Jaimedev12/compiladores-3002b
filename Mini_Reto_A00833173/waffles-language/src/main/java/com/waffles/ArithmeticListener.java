// Generated from Arithmetic.g4 by ANTLR 4.13.2
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link ArithmeticParser}.
 */
public interface ArithmeticListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link ArithmeticParser#prog}.
	 * @param ctx the parse tree
	 */
	void enterProg(ArithmeticParser.ProgContext ctx);
	/**
	 * Exit a parse tree produced by {@link ArithmeticParser#prog}.
	 * @param ctx the parse tree
	 */
	void exitProg(ArithmeticParser.ProgContext ctx);
	/**
	 * Enter a parse tree produced by {@link ArithmeticParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterExpr(ArithmeticParser.ExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link ArithmeticParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitExpr(ArithmeticParser.ExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link ArithmeticParser#term}.
	 * @param ctx the parse tree
	 */
	void enterTerm(ArithmeticParser.TermContext ctx);
	/**
	 * Exit a parse tree produced by {@link ArithmeticParser#term}.
	 * @param ctx the parse tree
	 */
	void exitTerm(ArithmeticParser.TermContext ctx);
	/**
	 * Enter a parse tree produced by {@link ArithmeticParser#factor}.
	 * @param ctx the parse tree
	 */
	void enterFactor(ArithmeticParser.FactorContext ctx);
	/**
	 * Exit a parse tree produced by {@link ArithmeticParser#factor}.
	 * @param ctx the parse tree
	 */
	void exitFactor(ArithmeticParser.FactorContext ctx);
}