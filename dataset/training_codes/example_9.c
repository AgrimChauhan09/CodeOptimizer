#include <stdio.h>

// Training example 9
int compute_9(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 9;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_9(100));
    return 0;
}
