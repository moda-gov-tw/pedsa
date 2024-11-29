using Microsoft.AspNetCore.Http;

namespace DeIdWeb_V2_K.Models
{
    public class FileInputModel
    {
        public IFormFile FileToUpload { get; set; }
    }
}
