// Generated from MyLang.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link MyLangParser}.
 */
public interface MyLangListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link MyLangParser#prog}.
	 * @param ctx the parse tree
	 */
	void enterProg(MyLangParser.ProgContext ctx);
	/**
	 * Exit a parse tree produced by {@link MyLangParser#prog}.
	 * @param ctx the parse tree
	 */
	void exitProg(MyLangParser.ProgContext ctx);
	/**
	 * Enter a parse tree produced by the {@code printExpr}
	 * labeled alternative in {@link MyLangParser#stat}.
	 * @param ctx the parse tree
	 */
	void enterPrintExpr(MyLangParser.PrintExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code printExpr}
	 * labeled alternative in {@link MyLangParser#stat}.
	 * @param ctx the parse tree
	 */
	void exitPrintExpr(MyLangParser.PrintExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code assignExpr}
	 * labeled alternative in {@link MyLangParser#stat}.
	 * @param ctx the parse tree
	 */
	void enterAssignExpr(MyLangParser.AssignExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code assignExpr}
	 * labeled alternative in {@link MyLangParser#stat}.
	 * @param ctx the parse tree
	 */
	void exitAssignExpr(MyLangParser.AssignExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code intExpr}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterIntExpr(MyLangParser.IntExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code intExpr}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitIntExpr(MyLangParser.IntExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code MulDiv}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterMulDiv(MyLangParser.MulDivContext ctx);
	/**
	 * Exit a parse tree produced by the {@code MulDiv}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitMulDiv(MyLangParser.MulDivContext ctx);
	/**
	 * Enter a parse tree produced by the {@code AddSub}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterAddSub(MyLangParser.AddSubContext ctx);
	/**
	 * Exit a parse tree produced by the {@code AddSub}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitAddSub(MyLangParser.AddSubContext ctx);
	/**
	 * Enter a parse tree produced by the {@code parensExpr}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterParensExpr(MyLangParser.ParensExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code parensExpr}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitParensExpr(MyLangParser.ParensExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code idExpr}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterIdExpr(MyLangParser.IdExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code idExpr}
	 * labeled alternative in {@link MyLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitIdExpr(MyLangParser.IdExprContext ctx);
}