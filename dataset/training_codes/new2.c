#include <stdio.h>

int sum_array_optimized(int *arr, int size) {
    int sum = 0;
    int i = 0;

    // Loop unrolling - process 2 elements per iteration
    for (; i < size - 1; i += 2) {
        sum += arr[i] + arr[i + 1];
    }

    // Handle leftover element if size is odd
    for (; i < size; i++) {
        sum += arr[i];
    }

    return sum;
}

int main() {
    int data[] = {1, 2, 3, 4, 5};
    int size = sizeof(data) / sizeof(data[0]);
    int result = sum_array_optimized(data, size);
    printf("Sum (Optimized): %d\n", result);
    return 0;
}