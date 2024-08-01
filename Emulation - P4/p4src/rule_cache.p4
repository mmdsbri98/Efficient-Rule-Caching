/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parsers.p4"

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

control MyIngress(inout headers hdr, 
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action regular_fwd(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
    }

    action get_self_action(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
        hdr.ipv4.protocol = hdr.cache_rule.protocol;
        hdr.cache_rule.setInvalid();
    }

    action get_cached_action(bit<9> egress_port) {
        hdr.cache_rule.ctype = C_TYPE_R;
        hdr.cache_rule.action_port = egress_port;
        standard_metadata.egress_spec = standard_metadata.ingress_port;
    }

    table forward_t {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            regular_fwd;
            NoAction;
        }
        size = 32;
        default_action = NoAction;
    }

    table cache_t {
        key = {
            hdr.cache_rule.owner: exact;
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            get_self_action;
            get_cached_action;
            NoAction;
        }
        size = 32;
        default_action = NoAction;
    }

    action query_pair(bit<9> action_port) {
       hdr.cache_rule.ctype = C_TYPE_Q1;
       standard_metadata.egress_spec = action_port;
    }
     
    action send_2ctrl(bit<9> action_port) {
       hdr.cache_rule.ctype = C_TYPE_Q2;
       standard_metadata.egress_spec = action_port;
    }

    table pairing_t {
        key = {
            hdr.cache_rule.ctype: exact;
        }
        actions = {
            query_pair;
            send_2ctrl;
            NoAction;
        }
        size = 32;
        default_action = NoAction;
    }

    action send_action_from_ctrl(bit<9> action_port, bit<9> response_port) {
       hdr.cache_rule.ctype = C_TYPE_R;
       hdr.cache_rule.action_port = action_port;
       standard_metadata.egress_spec = response_port;
    }

    table ctrl_t {
        key = {
            standard_metadata.ingress_port: exact;
            hdr.cache_rule.owner: exact;
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            send_action_from_ctrl;
            NoAction;
        }
        size = 32;
        default_action = NoAction;
    }

    apply {
        if (hdr.cache_rule.isValid() && hdr.cache_rule.ctype == C_TYPE_Q2) {
            ctrl_t.apply();
        } else if (hdr.cache_rule.isValid() && hdr.cache_rule.ctype == C_TYPE_R) {
	    standard_metadata.egress_spec = hdr.cache_rule.action_port;
            hdr.ipv4.protocol = hdr.cache_rule.protocol;
            hdr.cache_rule.setInvalid();
        } else if (!hdr.cache_rule.isValid() && !forward_t.apply().hit) {
            hdr.cache_rule.setValid();
            hdr.cache_rule.protocol = hdr.ipv4.protocol;
            hdr.ipv4.protocol = 7;
            hdr.cache_rule.owner = 0;
            hdr.cache_rule.ctype = C_TYPE_L;
        }
        if (hdr.cache_rule.isValid() && (hdr.cache_rule.ctype == C_TYPE_L || hdr.cache_rule.ctype == C_TYPE_Q1)) {
            if (hdr.cache_rule.ctype == C_TYPE_Q1) {
                hdr.cache_rule.owner = standard_metadata.ingress_port;
            }
            if (!cache_t.apply().hit) {
                pairing_t.apply();
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    apply { }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.dscp,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
