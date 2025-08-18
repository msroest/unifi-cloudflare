terraform {
  required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
      version = "5.8.4"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

terraform {
  backend "local" {
    path = "/state/terraform.tfstate"
  }
}