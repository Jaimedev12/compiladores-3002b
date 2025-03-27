package Tarea1.examples;

import java.util.Stack;

public class StackExample {
    public static void stackOperations(Integer[] nums) {
        Stack<Integer> stack = new Stack<>();

        for (Integer num : nums) {
            System.out.println("Pushing: " + num);
            stack.push(num);
        }

        System.out.println("Stack: " + stack);

        System.out.println("Popped: " + stack.pop());
        System.out.println("Top Num: " + stack.peek());
    }

    public static void main(String[] args) {
        System.out.println("Running Stack Example:");
        Integer[] sampleData = {1, 2, 3, 4};
        stackOperations(sampleData);
    }
}
