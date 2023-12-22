using Microsoft.AspNetCore.Http;

namespace DeIdWeb.Models
{
    public class FileInputModel
    {
        public IFormFile FileToUpload { get; set; }
    }
}
