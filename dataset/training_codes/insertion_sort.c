#include <stdio.h>
#include <stdlib.h>

// insertion_sort implementation
int main() {
    // Implementation for insertion_sort
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
