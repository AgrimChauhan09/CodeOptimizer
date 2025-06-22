#include <stdio.h>

int sum_array_unoptimized(int *arr, int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        // Redundant operation inside loop (multiplying by 1)
        sum += arr[i] * 1;
    }
    return sum;
}

int main() {
    int data[] = {1, 2, 3, 4, 5};
    int size = sizeof(data) / sizeof(data[0]);
    int result = sum_array_unoptimized(data, size);
    printf("Sum (Unoptimized): %d\n", result);
    return 0;
}