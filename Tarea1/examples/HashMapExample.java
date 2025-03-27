package Tarea1.examples;

import java.util.HashMap;

public class HashMapExample {
    public static void hashMapOperations() {
        HashMap<String, Integer> studentGrades = new HashMap<>();

        System.out.println("HashMap after adding grades: " + studentGrades);

        studentGrades.put("Alice", 90);
        studentGrades.put("Bob", 85);
        studentGrades.put("Charlie", 92);

        System.out.println("HashMap after adding grades: " + studentGrades);

        System.out.println("Bob's Grade: " + studentGrades.get("Bob"));
        System.out.println("Contains 'Alice': " + studentGrades.containsKey("Alice"));
    }

    public static void main(String[] args) {
        System.out.println("Running HashMap Example:");
        hashMapOperations();
    }
}
