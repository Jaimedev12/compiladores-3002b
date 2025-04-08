package mylang;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;

import java.util.HashMap;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        String input = "a = 1 + 2 * 3;\nprint a;";
        ANTLRInputStream inputStream = new ANTLRInputStream(input);
        MyLangLexer lexer = new MyLangLexer(inputStream);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        MyLangParser parser = new MyLangParser(tokens);
        ParseTree tree = parser.prog();

        EvalVisitor eval = new EvalVisitor();
        eval.visit(tree);
    }
}

// Simple interpreter using a visitor pattern
class EvalVisitor extends MyLangBaseVisitor<Integer> {
    Map<String, Integer> memory = new HashMap<>();

    @Override
    public Integer visitAssignExpr(MyLangParser.AssignExprContext ctx) {
        String id = ctx.ID().getText();
        int value = visit(ctx.expr());
        memory.put(id, value);
        return value;
    }

    @Override
    public Integer visitPrintExpr(MyLangParser.PrintExprContext ctx) {
        String id = ctx.ID().getText();
        int value = memory.getOrDefault(id, 0);
        System.out.println(value);
        return 0;
    }

    @Override
    public Integer visitMulDiv(MyLangParser.MulDivContext ctx) {
        int left = visit(ctx.expr(0));
        int right = visit(ctx.expr(1));
        return ctx.op.getType() == MyLangParser.MUL ? left * right : left / right;
    }

    @Override
    public Integer visitAddSub(MyLangParser.AddSubContext ctx) {
        int left = visit(ctx.expr(0));
        int right = visit(ctx.expr(1));
        return ctx.op.getType() == MyLangParser.ADD ? left + right : left - right;
    }

    @Override
    public Integer visitIntExpr(MyLangParser.IntExprContext ctx) {
        return Integer.valueOf(ctx.INT().getText());
    }

    @Override
    public Integer visitIdExpr(MyLangParser.IdExprContext ctx) {
        return memory.getOrDefault(ctx.ID().getText(), 0);
    }

    @Override
    public Integer visitParensExpr(MyLangParser.ParensExprContext ctx) {
        return visit(ctx.expr());
    }
}
