FT_STATUS_ftstatus;
FT_DEVICE_LIST_INFO_NODE* devInfo;
DWORD numDevs; // creates the device information list

ftStatus = FT_CreateDeviceInfoList(&numDevs); // allocate storage for list based on numDevs

devInfo = (FT_DEVICE_LIST_INFO_NODE*)malloc(sizeof(FT_DEVICE_LIST_INFO_NODE)*numDevs);
// get the device information list

ftStatus = FT_GetDeviceInfoList(devInfo,&numDevs);
FT_HANDLE handle;

int i;
for (i = 0; i < numDevs; i++){
    if ((devInfo[i].ID & 0xFFFF == 0x89D4)){
        ftStatus  = FT_Open(i, &handle);
        ftStatus = FT_SetBitMode(handle, 0x00, 0x40);
        break;
    }
    
}
