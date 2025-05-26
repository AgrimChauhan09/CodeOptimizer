#include <stdio.h>
#include <stdlib.h>

// numerical_methods implementation
int main() {
    // Implementation for numerical_methods
    int data[100];
    for (int i = 0; i < 100; i++) {
        data[i] = i * 2;
    }
    
    int result = 0;
    for (int i = 0; i < 100; i++) {
        result += data[i] * data[i];
    }
    
    printf("Result: %d\n", result);
    return 0;
}
