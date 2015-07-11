#!/usr/bin/python
#
# Copyright (c) 2015 Juniper Networks, Inc. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

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
        fqn = ['default-domain', 'default-project', uuid]
        table = client.interface_route_table_read(fq_name=fqn)
        routes = table.get_interface_route_table_routes()
        for rt in routes.route:
            if rt.prefix == subnet:
                logging.error('Duplicate prefix')
                sys.exit(1)
        routes.add_route(opencontrail.RouteType(subnet, None, None))
        table.set_interface_route_table_routes(routes)
        client.interface_route_table_update(table)

        refs = vmi.get_interface_route_table_refs()
        found = False
        for ref in refs:
            if ref['uuid'] == table.uuid:
                found = True
                break
        if not found:
            vmi.add_interface_route_table(table)
            client.virtual_machine_interface_update(vmi)

    except opencontrail.NoIdError:
        logging.debug('Create route-table')
        table = opencontrail.InterfaceRouteTable(name=uuid)
        routes = opencontrail.RouteTableType()
        routes.add_route(opencontrail.RouteType(subnet, None, None))
        table.set_interface_route_table_routes(routes)
        client.interface_route_table_create(table)
        vmi.add_interface_route_table(table)
        client.virtual_machine_interface_update(vmi)


def interface_del_route(client, uuid, subnet):
    try:
        vmi = client.virtual_machine_interface_read(id=uuid)
    except opencontrail.NoIdError:
        logging.error('Interface not found')
        sys.exit(0)

    try:
        fqn = ['default-domain', 'default-project', uuid]
        table = client.interface_route_table_read(fq_name=fqn)
    except opencontrail.NoIdError:
        return

    if subnet is None:
        vmi.del_interface_route_table(table)
        client.virtual_machine_interface_update(vmi)
        client.interface_route_table_delete(id=table.uuid)
        return

    routes = table.get_interface_route_table_routes()
    routes.delete_route(opencontrail.RouteType(subnet, None, None))
    if len(routes.route) == 0:
        vmi.del_interface_route_table(table)
        client.virtual_machine_interface_update(vmi)
        client.interface_route_table_delete(id=table.uuid)
    else:
        table.set_interface_route_table_routes(routes)
        client.interface_route_table_update(table)


def interface_show_route(client, uuid):
    try:
        vmi = client.virtual_machine_interface_read(id=uuid)
    except opencontrail.NoIdError:
        print 'Interface not found\n'
        return

    refs = vmi.get_interface_route_table_refs()
    if refs is None:
        print 'Interface has no route table configured'
        return

    table = None
    for ref in refs:
        fqn = ref['to']
        if fqn[len(fqn) - 1] == uuid:
            try:
                table = client.interface_route_table_read(id=ref['uuid'])
            except opencontrail.NoIdError:
                pass
            break
    if not table:
        print 'No interface route table'
        return

    print 'Interface static routes for %s' % vmi.display_name
    routes = table.get_interface_route_table_routes()
    for rt in routes.route:
        print '  %s' % rt.prefix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user',
                        help='Admin user (e.g. KEYSTONE admin_user)',
                        default='admin')
    parser.add_argument('-t', '--tenant',
                        help='Admin tenant (e.g. KEYSTONE admin_tenant_name)',
                        default='admin')
    parser.add_argument('-w', '--password',
                        help='Admin password (e.g. KEYSTONE admin_password)')
    parser.add_argument('-s', '--server',
                        help='OpenContrail API server',
                        default='localhost')
    parser.add_argument('-p', '--port', default='8082')

    subparsers = parser.add_subparsers(title='command', dest='command')
    add_parser = argparse.ArgumentParser(add_help=False)

    add_parser.add_argument('uuid', help='Interface (neutron port) uuid')
    add_parser.add_argument('subnet', help='IP subnet prefix')

    del_parser = argparse.ArgumentParser(add_help=False)
    del_parser.add_argument('uuid', help='Interface (neutron port) uuid')
    del_parser.add_argument('subnet', nargs='?',
                            help='IP subnet prefix to delete (optional). '
                            'When not specified all routes are deleted')

    show_parser = argparse.ArgumentParser(add_help=False)
    show_parser.add_argument('uuid', help='Interface (neutron port) uuid')

    subparsers.add_parser('add', parents=[add_parser])
    subparsers.add_parser('delete', parents=[del_parser])
    subparsers.add_parser('show', parents=[show_parser])

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
        interface_del_route(client, args.uuid, args.subnet)
    elif args.command == 'show':
        interface_show_route(client, args.uuid)
    else:
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logging.error(ex)
