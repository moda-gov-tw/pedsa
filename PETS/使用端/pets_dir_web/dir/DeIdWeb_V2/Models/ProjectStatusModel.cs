using System;

namespace PETs_Dir.Models
{
    public class ProjectStatusModel
    {
        public int ps_id { get; set; }
        public int project_id { get; set; }
        public int createMember_Id { get; set; }
        public int updateMember_Id { get; set; }
        public int project_status { get; set; }
        public string statusname { get; set; }
        public string key_code { get; set; }
        public string service_ip { get; set; }
        public string dataset_name { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
    }
}
