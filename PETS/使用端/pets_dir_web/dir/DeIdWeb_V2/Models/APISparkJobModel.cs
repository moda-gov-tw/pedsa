using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2.Models
{
    public class APISparkJobModel
    {
    
        public string applicationID { get; set; }
    
    }

    public class APIProjectNameModel
    {

        public string userId { get; set; }
        public string userAccount { get; set; }
        public string proj_name { get; set; }

    }

    public class APIProjectDateTimeModel
    {

        public string dateTime { get; set; }

    }
}
