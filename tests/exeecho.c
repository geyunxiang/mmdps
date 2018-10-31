#include <stdio.h>

int main(int argc, char *argv[]) {
	printf("In exe\n");
	for (int i = 0; i < argc; ++i) {
		printf("%s ", argv[i]);
	}
	printf("\n");
}
