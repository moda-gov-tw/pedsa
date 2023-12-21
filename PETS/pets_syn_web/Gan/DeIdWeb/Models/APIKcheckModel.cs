using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class APIKcheckModel
    {
        public string projID { get; set; }
        public string projStep { get; set; }
        public string projName { get; set; }

        public string jobName { get; set; }
        public int kchecking { get; set; }
        public APIKcheckMainInfoModel mainInfo { get; set; }
    }

    public class APIKcheckMainInfoModel
    {
        public string joinType { get; set; }
        public string kValue { get; set; }
      //  public string jobName { get; set; }
        public string publicTableName { get; set; }
        public JArray dataInfo { get; set; }
    }

    public class KcheckdataInfoModel
    {
        public string[] QIcols { get; set; }
        public string[] colNames { get; set; }
        public string tableName { get; set; }
        public string dbName { get; set; }
        public string[] keyNames { get; set; }
    }


}
