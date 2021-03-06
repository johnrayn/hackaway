#include "mstring.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

void append(char *str1, char *str2, char **result) {
    int len1 = strlen(str1);
    int len2 = strlen(str2);

    *result = malloc(len1 + len2 + 1);
    for (int i = 0; i < len1; i++) {
        (*result)[i] = str1[i];
    }
    for (int i = 0; i < len2; i++) {
        (*result)[i + len1] = str2[i];
    }
    (*result)[len1+len2] = '\0';
}

void free_append(char *result) {
    free(result);
}


void split(char *str, char sep, char ***result) {
    char *p = str;
    int count = 1;
    while (*p != '\0'){
        if (*p == sep){
            count++;
        }
        p++;
    } // end while

    // number of parts
    char **parts = malloc((count+1) * sizeof(char *));
    *(parts + count) = NULL;

    int head, tail;
    head = tail = 0;
    for (int i = 0; i < count; i++) {
        char *p = &str[head];
        while (*p != sep && *p != '\0') {
            tail++;
            p++;
        }
        int len = tail - head;
        
        char *tmpstr = malloc(len + 1);
        for (int i = 0; i < len; i++) {
            tmpstr[i] = str[i+head];
        }
        tmpstr[len] = '\0';
        head = tail + 1;  tail = head;
        *(parts + i) = tmpstr;
        
    }
    *result = parts;
}

void free_split(char **result){
    char **p = result;
    while (*p != NULL) {
        free(*p++);
    }
    free(result);
}


void replace(char *str, char *pattern, char **result){
    // wait for implement
}

void free_replace(char *result){
    free(result);
}


int equal(char *str1, char *str2){

    while (*str1 != '\0' && *str2 !='\0') {
        if (*str1 != *str2) {
            return 0;
        } else {
            str1++; str2++;
        }
    }
    if (*str1 == '\0' && *str2 == '\0')
        return 1;
    else
        return 0;
}



void join(char **strlist, char *sep, char **result) {
    // wait for implement
}
void free_join(char *result) {
    free(result);
}


void substr(char *str, char *substr, int ***xys) {
    // wait for implement
}
void free_substr(int **xys) {
    // wait for implement
}

void strip(char *str, char **result) {
    int start = 0, end;
    int i = 0;
    // find the start index
    while (str[i] != '\0') {
        if (str[i] != ' ') {
            break;
        }
        i++;
        start++;
    }
    // find the end index
    end = start + 1;
    i++;
    while (str[i] != '\0') {
        if (str[i] != ' ') {
            end = i + 1;
        }
        i++;
    }
    // copy to new string.
    int len = end - start;
    *result = malloc(len + 1);
    for (int i = 0; i < len; i++) {
        (*result)[i] = str[i+start]; 
    }
    (*result)[len] = '\0';
}

void free_strip(char *result) {
    free(result);
}