using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2.Models
{

    /// <summary>
    /// appStatus.app
    /// </summary>
    public class AppProjectStatusModel
    {
        
        
        public string project_name { get; set; }
        public string pro_tb { get; set; }
        public string member_id { get; set; }
  
        public string Application_Name { get; set; }
        public string App_State { get; set; }
        public string Progress { get; set; }
        public string Progress_State { get; set; }
      
        public DateTime? enddate { get; set; }
        public DateTime createtime { get; set; }
        public string worktime { get; set; }
    }
}
