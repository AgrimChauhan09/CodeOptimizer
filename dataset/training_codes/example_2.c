#include <stdio.h>

// Training example 2
int compute_2(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 2;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_2(100));
    return 0;
}
