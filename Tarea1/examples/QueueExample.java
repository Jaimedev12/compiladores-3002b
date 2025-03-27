package Tarea1.examples;

import java.util.LinkedList;
import java.util.Queue;

public class QueueExample {
    public static void queueOperations(Integer[] nums) {
        Queue<Integer> queue = new LinkedList<>();

        for (Integer num : nums) {
            System.out.println("Adding: " + num);
            queue.add(num);
        }

        System.out.println("Queue: " + queue);

        System.out.println("Removed: " + queue.poll());
        System.out.println("Front element: " + queue.peek());
    }

    public static void main(String[] args) {
        System.out.println("Running Queue Example:");
        queueOperations(new Integer[] {1, 2, 3, 4, 5});
    }
}
