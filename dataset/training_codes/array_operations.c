#include <stdio.h>

int find_max(int arr[], int n) {
    int max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}

int main() {
    int arr[] = {3, 5, 7, 2, 8, 6, 4, 10, 12, 1};
    int n = sizeof(arr) / sizeof(arr[0]);
    printf("Maximum element: %d\n", find_max(arr, n));
    return 0;
}
