Handle hSerial = CreateFile(  "\\\\.\\COM6",
                              GENERIC_READ|GENERIC_WRITE,
                              0,
                              NULL,
                              OPEN_EXISTING,
                              FILE_ATTRIBUTE_NORMAL,
                              NULL );
if (hSerial == INVALID_HANDLE_VALUE) {
fprintf(stderr, "Error\n"); return 0;
}
return 1;