using Microsoft.AspNetCore.Http;

namespace DeIdWeb_V2.Models
{
    public class FileInputModel
    {
        public IFormFile FileToUpload { get; set; }
    }
}
