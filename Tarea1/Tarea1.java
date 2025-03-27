package Tarea1;

import Tarea1.examples.QueueExample;
import Tarea1.examples.StackExample;
import Tarea1.examples.HashMapExample;

public class Tarea1 {
    public static void main(String[] args) {
        System.out.println("Running All Examples:\n");

        QueueExample.main(args);
        System.out.println();
        StackExample.main(args);
        System.out.println();
        HashMapExample.main(args);
    }
}
