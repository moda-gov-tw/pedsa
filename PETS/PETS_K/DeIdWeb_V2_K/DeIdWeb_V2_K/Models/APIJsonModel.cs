using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class APIModel
    {
        
        public string jsonBase64 { get; set; }
        
    }
    public class GetServerFolderJsonModel
    {
        //"{\"projName\": \"test_project\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}"
        public string projName { get; set; }
        public string projStep { get; set; }
        public string projID { get; set; }
        public string userAccount { get; set; }
        public string userId { get; set; }
    }

    public class ImortDataJsonModel
    {

    }

    public class mlresult_report
    {
        public string model_name { get; set; }
        public string ts { get; set; }
        public string vs { get; set; }

    }

    public class MLDataModelAPI
    {
        public string projID { get; set; }
        public string userID { get; set; }
        public string projName { get; set; }
        public string rawTbl { get; set; }
        public string deIdTbl { get; set; }
        public string[] targetCols { get; set; }
    }
    }
