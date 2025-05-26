#include <stdio.h>

// Training example 5
int compute_5(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 5;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_5(100));
    return 0;
}
