using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2.Models
{

    /// <summary>
    /// appStatus.app
    /// </summary>
    public class AppStatusModel
    {
        public int id { get; set; }
        public int isRead { get; set; }
        public string Application_Id { get; set; }
        public string project_cht { get; set; }
        public string tbname { get; set; }
        public string Application_Name { get; set; }
        public string Application_State { get; set; }
        public string Progress { get; set; }
        public string Progress_State { get; set; }
        public string proj_id { get; set; }
        public string dbname { get; set; }
        public DateTime Createtime { get; set; }
        public DateTime statustime { get; set; }
        public DateTime Updatetime { get; set; }
    }
}
