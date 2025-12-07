require 'net/http'
require 'json'

module AntiProxy
  API_URL = 'https://proxycheck.io/v2/'.freeze
  API_KEY = nil

  def self.is_proxy?(ip)
    uri = URI("#{API_URL}#{ip}?vpn=1&asn=1")
    uri.query = URI.encode_www_form({key: API_KEY}) if API_KEY
    response = Net::HTTP.get(uri)
    data = JSON.parse(response)
    result = data[ip]
    return false unless result && result['proxy']
    result['proxy'] == 'yes'
  rescue StandardError => e
    warn "AntiProxy check failed: #{e.message}"
    false
  end
end
