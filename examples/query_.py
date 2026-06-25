from fetch_bio import  get_bio_info, query_bioportal, query_uniprot, get_bio_info_batch


print("http://purl.obolibrary.org/obo/GO_0055056", get_bio_info("http://purl.obolibrary.org/obo/GO_0055056"))
print("http://purl.uniprot.org/uniprot/P11168", get_bio_info("http://purl.uniprot.org/uniprot/P11168"))
print("FMA:66836", get_bio_info("FMA:66836"))
print("PR:Q924C9", get_bio_info("PR:Q924C9"))
print("UBERON:0000955", get_bio_info("UBERON:0000955"))
print("CHEBI:4167", get_bio_info("CHEBI:4167"))
print("Q02013", get_bio_info("Q02013"))
print ("SBO:0000014", get_bio_info("SBO:0000014"))
print("CL:0000540", get_bio_info("CL:0000540"))

list_of_uris = [
    "http://purl.obolibrary.org/obo/GO_0055056",
    "http://purl.uniprot.org/uniprot/P11168",
    "FMA:66836",
    "PR:Q924C9",
    "UBERON:0000955"]

print(get_bio_info_batch(list_of_uris, json_output="bio_info_batch.json"))