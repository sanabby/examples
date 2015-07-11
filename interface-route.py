#!/usr/bin/python

import argparse
import logging
import sys

import vnc_api.vnc_api as opencontrail

def interface_add_route(client, uuid, subnet):
    try:
        vmi = client.virtual_machine_interface_read(id=uuid)
    except opencontrail.NoIdError:
        logging.error('Interface not found')
        sys.exit(1)

    try:
        table = client.interface_route_table_read(name=uuid)
    except opencontrail.NoIdError:
        logging.debug('Create route-table')
        table = opencontrail.InterfaceRouteTable()
        routes = opencontrail.RouteTableType()
        routes.add_route(opencontrail.RouteType(subnet, None, None))
        table.set_interface_route_table_routes(routes)
        client.interface_route_table_create(table)
        vmi.add_interface_route_table(table)
        client.virtual_machine_interface_update(vmi)        

def interface_del_route(client, uuid):
    try:
        vmi = client.virtual_machine_interface_read(id=uuid)
    except opencontrail.NoIdError:
        sys.exit(0)
    vmi.set_interface_route_table_list(None)
    client.virtual_machine_interface_update(vmi)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', default='admin')
    parser.add_argument('-t', '--tenant', default='admin')
    parser.add_argument('-w', '--password')
    parser.add_argument('-s', '--server', default='localhost')
    parser.add_argument('-p', '--port', default='8082')

    subparsers = parser.add_subparsers(title='command', dest='command')

    add_parser = argparse.ArgumentParser(add_help=False)
    add_parser.add_argument('uuid')
    add_parser.add_argument('subnet')

    del_parser = argparse.ArgumentParser(add_help=False)
    del_parser.add_argument('uuid')

    subparsers.add_parser('add', parents=[add_parser])
    subparsers.add_parser('delete', parents=[del_parser])

    args = parser.parse_args()

    client = None
    if args.password:
        client = opencontrail.VncApi(args.user, args.password, args.tenant,
                                     api_server_host=args.server,
                                     api_server_port=args.port)
    else:
        client = opencontrail.VncApi(api_server_host=args.server,
                                     api_server_port=args.port)

    if args.command == 'add':
        interface_add_route(client, args.uuid, args.subnet)
    elif args.command == 'delete':
        interface_del_route(client, args.uuid)
    else:
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logging.error(ex)
