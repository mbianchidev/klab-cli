variable "ebs_volume" {
  default = {
    ebs1 = {
      availability_zone = "eu-west-1a"
      encrypted = true
      size = 40
      type = "gp2"
    }
    ebs2 = {
      availability_zone = "eu-west-1b"
      encrypted = true
      size = 30
      type = "standard"
    }
  }
}