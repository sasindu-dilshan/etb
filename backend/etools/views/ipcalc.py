from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

import csv
import ipaddress


class SingleIPCalculatorAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        ip = request.data.get('ip')
        subnet = request.data.get('subnet')
        version = request.data.get('version')

        try:
            result = self.get_ip_info(ip, subnet, version)
            return JsonResponse(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_ip_info(self, ip, subnet, version):
        if version.lower() == 'ipv4':
            if '/' in subnet:
                subnet_mask = subnet.split('/')[-1]
            else:
                subnet_mask = subnet
            network = ipaddress.IPv4Network(ip + '/' + subnet_mask, strict=False)
            result = {
                "IP_Address": str(network.network_address),
                "Full_IP_Address": str(network.network_address) + '/' + subnet_mask,
                "Total_IP_Addresses": network.num_addresses,
                "Network": str(network.network_address) + '/' + str(network.prefixlen),
                "First_IP": str(network.network_address + 1),
                "Last_IP": str(network.broadcast_address - 1),
                "Netmask": str(network.netmask),
                "Hostmask": str(network.hostmask),
                "Broadcast_IP": str(network.broadcast_address),
                "Is_Private": network.is_private,
                "Is_Public": not network.is_private,
           }
        elif version.lower() == 'ipv6':
            try:
                network = ipaddress.IPv6Network(ip + '/' + subnet, strict=False)
                result = {
                    "IP_Address": str(network.network_address),
                    "Full_IP_Address": ip + '/' + subnet,
                    "Total_IP_Addresses": network.num_addresses,
                    "Network": str(network.network_address) + '/' + str(network.prefixlen),
                    "First_IP": str(network.network_address + 1),
                    "Last_IP": str(network.broadcast_address - 1),
                    "Prefix_Length": network.prefixlen,
                    "Is_Link_Local": network.is_link_local,
                    "Is_Site_Local": network.is_site_local,
                    "Is_Global": not network.is_link_local and not network.is_site_local
                }
            except ValueError as e:
                raise ValueError("Invalid IPv6 address or subnet length.")
        else:
            raise ValueError("Invalid IP version. Only 'ipv4' and 'ipv6' are supported.")

        return result

class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class BatchIPCalculatorAPIView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)
        if serializer.is_valid():
            # Get the uploaded file
            uploaded_file = request.FILES['file']

            # Process the CSV data
            try:
                decoded_file = uploaded_file.read().decode('utf-8')
                csv_reader = csv.DictReader(decoded_file.splitlines())

                # Iterate through the CSV rows
                results = []
                single_ip_calculator = SingleIPCalculatorAPIView()  # Create an instance of SingleIPCalculatorAPIView
                
                for row in csv_reader:
                    row = {key.strip('\ufeff'): value for key, value in row.items()}
                    if 'IP_Address' in row and 'Subnet_Mask' in row and 'IP_Version' in row:
                        ip_address = row['IP_Address']
                        subnet_mask = row['Subnet_Mask']
                        ip_version = row['IP_Version'].lower()
                        
                        try:
                            # Call the get_ip_info function from the SingleIPCalculatorAPIView instance
                            result = single_ip_calculator.get_ip_info(ip_address, subnet_mask, ip_version)
                            results.append(result)
                        except Exception as e:
                            results.append({'error': str(e)})
                            print(f'Error processing row: {row}')

                return JsonResponse(results, status=status.HTTP_201_CREATED, safe=False)
            except Exception as e:
                return JsonResponse({'error': 'Error processing CSV data', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
