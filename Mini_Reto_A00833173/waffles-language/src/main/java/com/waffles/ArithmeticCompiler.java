package com.waffles;

import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.Token;
import com.waffles.lexer_files.ArithmeticLexer;

public class ArithmeticCompiler {
    public static void main(String[] args) {
        String input = "3 + 5 * 2";

        System.out.println(input);

        // Lexical analysis
        CharStream inputStream = CharStreams.fromString(input);
        ArithmeticLexer lexer = new ArithmeticLexer(inputStream);
        CommonTokenStream tokens = new CommonTokenStream(lexer);

        // Print tokens
        for (Token token : tokens.getTokens()) {
            System.out.println("Token: " + token.getText() + " (" + lexer.getVocabulary().getSymbolicName(token.getType()) + ")");
        }
    }
}
