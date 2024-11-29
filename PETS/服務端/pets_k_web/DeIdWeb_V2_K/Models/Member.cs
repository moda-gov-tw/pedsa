using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class Member
    {
        public int Id { get; set; }
        public int dept_id { get; set; }
        public string UserAccount { get; set; }
        public string UserName { get; set; }
        public string Password { get; set; }
        public string dept_name { get; set; }
        public string Email { get; set; }
        //public string Email { get; set; }
        public int IsAdmin { get; set; }
        public string isAdminNM { get; set; }
        public DateTime Createtime { get; set; }
        public DateTime Updatetime { get; set; }
    }

    public class memberIdAdmin
    {
        public int value { get; set; }
        public string isAdmin { get; set; }
    }
}
