using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class APIModel
    {
        
        public string jsonBase64 { get; set; }
        
    }
    public class GetServerFolderJsonModel
    {
        //"{\"projName\": \"test_project\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}"
     public   string projName { get; set; }
        public string projStep { get; set; }
        public string projID { get; set; }
    }

    public class createFolderAPI            
    {
        public string userID { get; set; }
        public string projID { get; set; }
        public string projName { get; set; }
    }

    public class ExportFileAPI
    {
        public string userID { get; set; }
        public string projID { get; set; }
        public string projName { get; set; }
        public string[] dataName { get; set; }
    }

    public class previewDataModelAPI
    {
        public string userID { get; set; }
        public string projID { get; set; }
        public string projName { get; set; }
        public string fileName { get; set; }
    }

    public class MLDataModelAPI
    {
        public string userID { get; set; }
        public string projID { get; set; }
        public string projName { get; set; }
        public string rawDataName { get; set; }
        public string[] targetCols { get; set; }
    }

    public class gansyncModelAPI
    {
        public string userID { get; set; }
        public string projID { get; set; }
        public string projName { get; set; }
        public string fileName { get; set; }
        public string[] colNames { get; set; }
        public string[] select_colNames { get; set; }
        public string[] keyName { get; set; }
      
    }

    public class mlresult_report
    {
        public string model_name { get; set; }
        public string ts { get; set; }
        public string vs { get; set; }
        
    }
}
