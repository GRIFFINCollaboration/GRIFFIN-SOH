
//#include <utils.h>
#include <midas.h>

extern char* frontend_name;
extern HNDLE hDB;

static HNDLE odbGetHandle(HNDLE hDB, HNDLE dir, char *name, int type)
{
  /* Find key in the ODB */
  HNDLE key;
  int status = db_find_key (hDB, dir, name, &key);
  if (type != 0 && status == DB_NO_KEY)
    {
      // create key if it does not exist
      status = db_create_key(hDB, dir, name, type);
      if (status != SUCCESS)
        {
          cm_msg (MERROR, frontend_name, "Cannot create \'%s\', error %d", name, status);
          abort();
          // NOT REACHED
          return 0;
        }
      status = db_find_key(hDB, dir, name, &key);
      cm_msg (MERROR, frontend_name, "Created ODB key \'%s\' of type %d", name, type);
    }

  if (status != SUCCESS)
    {
      if (dir==0)
        cm_msg (MERROR, frontend_name, "Cannot find odb handle for \'%s\', error %d", name, status);
      else
        cm_msg (MERROR, frontend_name, "Cannot find odb handle for %d/\'%s\', error %d", dir, name, status);
      abort();
      // NOT REACHED
      return 0;
    }

  return key;
}

static int odbReadAny(const char*name,int index,int tid,void* value,int valueLength = 0)
{
  int status;
  int size = rpc_tid_size(tid);
  HNDLE hdir = 0;
  HNDLE hkey;

  if (valueLength > 0)
    size = valueLength;

  status = db_find_key (hDB, hdir, (char*)name, &hkey);
  if (status == SUCCESS)
    {
      status = db_get_data_index(hDB, hkey, value, &size, index, tid);
      if (status != SUCCESS)
        {
          cm_msg(MERROR, frontend_name, "Cannot read \'%s\'[%d] of type %d from odb, db_get_data_index() status %d", name, index, tid, status);
          return -1;
        }

      return 0;
    }
  else if (status == DB_NO_KEY)
    {
      cm_msg(MINFO, frontend_name, "Creating \'%s\'[%d] of type %d", name, index, tid);

      status = db_create_key(hDB, hdir, (char*)name, tid);
      if (status != SUCCESS)
        {
          cm_msg (MERROR, frontend_name, "Cannot create \'%s\' of type %d, db_create_key() status %d", name, tid, status);
          return -1;
        }

      status = db_find_key (hDB, hdir, (char*)name, &hkey);
      if (status != SUCCESS)
        {
          cm_msg(MERROR, frontend_name, "Cannot create \'%s\', db_find_key() status %d", name, status);
          return -1;
        }

      status = db_set_data_index(hDB, hkey, value, size, index, tid);
      if (status != SUCCESS)
        {
          cm_msg(MERROR, frontend_name, "Cannot write \'%s\'[%d] of type %d to odb, db_set_data_index() status %d", name, index, tid, status);
          return -1;
        }

      return 0;
    }
  else
    {
      cm_msg(MERROR, frontend_name, "Cannot read \'%s\'[%d] from odb, db_find_key() status %d", name, index, status);
      return -1;
    }
};

static int odbReadInt(const char*name,int index = 0,int defaultValue = 0)
{
  int value = defaultValue;
  if (odbReadAny(name,index,TID_INT,&value) == 0)
    return value;
  else
    return defaultValue;
};

static uint32_t odbReadUint32(const char*name,int index = 0,uint32_t defaultValue = 0)
{
  uint32_t value = defaultValue;
  if (odbReadAny(name,index,TID_DWORD,&value) == 0)
    return value;
  else
    return defaultValue;
};

static double odbReadDouble(const char*name,int index = 0,double defaultValue = 0)
{
  double value = defaultValue;
  if (odbReadAny(name,index,TID_DOUBLE,&value) == 0)
    return value;
  else
    return defaultValue;
};

static float odbReadFloat(const char*name,int index = 0,double defaultValue = 0)
{
  float value = defaultValue;
  if (odbReadAny(name,index,TID_FLOAT,&value) == 0)
    return value;
  else
    return defaultValue;
};

static bool     odbReadBool(const char*name,int index = 0,bool defaultValue = 0)
{
  uint32_t value = defaultValue;
  if (odbReadAny(name,index,TID_BOOL,&value) == 0)
    return value;
  else
    return defaultValue;
};

static const char* odbReadString(const char*name,int index,const char* defaultValue,int stringLength)
{
  const int maxStringLength = 256;
  static char buf[maxStringLength];
  buf[0] = 0;
  if (defaultValue)
    strlcpy(buf, defaultValue, maxStringLength);
  assert(stringLength < maxStringLength);
  if (odbReadAny(name, index, TID_STRING, buf, stringLength) == 0)
    return buf;
  else
    return defaultValue;
};

static int odbReadArraySize(const char*name)
{
  int status;
  HNDLE hdir = 0;
  HNDLE hkey;
  KEY key;

  status = db_find_key (hDB, hdir, (char*)name, &hkey);
  if (status != SUCCESS)
    return 0;

  status = db_get_key(hDB, hkey, &key);
  if (status != SUCCESS)
    return 0;

  return key.num_values;
}

static int odbWriteInt(const char*name, int index, int value)
{
  int status;
  HNDLE hdir = 0;
  HNDLE hkey;

  status = db_find_key (hDB, hdir, name, &hkey);
  if (status == SUCCESS)
    {
      int size = 4;
      status = db_set_data_index(hDB, hkey, &value, size, index, TID_INT);
      if (status == SUCCESS)
	return 0;
    }

  return -1;
}

static int odbWriteBool(const char*name, int index, bool value)
{
  int status;
  HNDLE hdir = 0;
  HNDLE hkey;

  status = db_find_key (hDB, hdir, (char*)name, &hkey);
  if (status == SUCCESS)
    {
      int size = 4;
      status = db_set_data_index(hDB, hkey, &value, size, index, TID_BOOL);
      if (status == SUCCESS)
	return 0;
    }

  return -1;
}

static int odbWriteDouble(const char*name, int index, double value)
{
  int status;
  HNDLE hdir = 0;
  HNDLE hkey;

  status = db_find_key (hDB, hdir, name, &hkey);
  if (status == SUCCESS)
    {
      int size = sizeof(double);
      status = db_set_data_index(hDB, hkey, &value, size, index, TID_DOUBLE);
      if (status == SUCCESS)
	return 0;
    }

  return -1;
}

static int odbWriteString(const char*name, const char* string)
{
  int status;
  HNDLE hdir = 0;
  HNDLE hkey;

  status = db_find_key(hDB, hdir, name, &hkey);
  if (status == SUCCESS)
    {
      int size = strlen(string) + 1;

      status = db_set_data(hDB, hkey, string, size, 1, TID_STRING);
      if (status == SUCCESS)
	return SUCCESS;
    }

  return status;
}


// end
