// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.27.1
// 	protoc        v3.5.1
// source: KibanaLog.proto

package __

import (
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type KibanaLog_PhoneType int32

const (
	KibanaLog_MOBILE KibanaLog_PhoneType = 0
	KibanaLog_HOME   KibanaLog_PhoneType = 1
	KibanaLog_WORK   KibanaLog_PhoneType = 2
)

// Enum value maps for KibanaLog_PhoneType.
var (
	KibanaLog_PhoneType_name = map[int32]string{
		0: "MOBILE",
		1: "HOME",
		2: "WORK",
	}
	KibanaLog_PhoneType_value = map[string]int32{
		"MOBILE": 0,
		"HOME":   1,
		"WORK":   2,
	}
)

func (x KibanaLog_PhoneType) Enum() *KibanaLog_PhoneType {
	p := new(KibanaLog_PhoneType)
	*p = x
	return p
}

func (x KibanaLog_PhoneType) String() string {
	return protoimpl.X.EnumStringOf(x.Descriptor(), protoreflect.EnumNumber(x))
}

func (KibanaLog_PhoneType) Descriptor() protoreflect.EnumDescriptor {
	return file_KibanaLog_proto_enumTypes[0].Descriptor()
}

func (KibanaLog_PhoneType) Type() protoreflect.EnumType {
	return &file_KibanaLog_proto_enumTypes[0]
}

func (x KibanaLog_PhoneType) Number() protoreflect.EnumNumber {
	return protoreflect.EnumNumber(x)
}

// Deprecated: Use KibanaLog_PhoneType.Descriptor instead.
func (KibanaLog_PhoneType) EnumDescriptor() ([]byte, []int) {
	return file_KibanaLog_proto_rawDescGZIP(), []int{0, 0}
}

type KibanaLog struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Name   string                   `protobuf:"bytes,1,opt,name=name,proto3" json:"name,omitempty"`
	Id     int32                    `protobuf:"varint,2,opt,name=id,proto3" json:"id,omitempty"` // Unique ID number for this person.
	Email  string                   `protobuf:"bytes,3,opt,name=email,proto3" json:"email,omitempty"`
	Phones []*KibanaLog_PhoneNumber `protobuf:"bytes,4,rep,name=phones,proto3" json:"phones,omitempty"`
}

func (x *KibanaLog) Reset() {
	*x = KibanaLog{}
	if protoimpl.UnsafeEnabled {
		mi := &file_KibanaLog_proto_msgTypes[0]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *KibanaLog) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*KibanaLog) ProtoMessage() {}

func (x *KibanaLog) ProtoReflect() protoreflect.Message {
	mi := &file_KibanaLog_proto_msgTypes[0]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use KibanaLog.ProtoReflect.Descriptor instead.
func (*KibanaLog) Descriptor() ([]byte, []int) {
	return file_KibanaLog_proto_rawDescGZIP(), []int{0}
}

func (x *KibanaLog) GetName() string {
	if x != nil {
		return x.Name
	}
	return ""
}

func (x *KibanaLog) GetId() int32 {
	if x != nil {
		return x.Id
	}
	return 0
}

func (x *KibanaLog) GetEmail() string {
	if x != nil {
		return x.Email
	}
	return ""
}

func (x *KibanaLog) GetPhones() []*KibanaLog_PhoneNumber {
	if x != nil {
		return x.Phones
	}
	return nil
}

// Our address book file is just one of these.
type AddressBook struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	People []*KibanaLog `protobuf:"bytes,1,rep,name=people,proto3" json:"people,omitempty"`
}

func (x *AddressBook) Reset() {
	*x = AddressBook{}
	if protoimpl.UnsafeEnabled {
		mi := &file_KibanaLog_proto_msgTypes[1]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *AddressBook) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*AddressBook) ProtoMessage() {}

func (x *AddressBook) ProtoReflect() protoreflect.Message {
	mi := &file_KibanaLog_proto_msgTypes[1]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use AddressBook.ProtoReflect.Descriptor instead.
func (*AddressBook) Descriptor() ([]byte, []int) {
	return file_KibanaLog_proto_rawDescGZIP(), []int{1}
}

func (x *AddressBook) GetPeople() []*KibanaLog {
	if x != nil {
		return x.People
	}
	return nil
}

type KibanaLog_PhoneNumber struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Number string              `protobuf:"bytes,1,opt,name=number,proto3" json:"number,omitempty"`
	Type   KibanaLog_PhoneType `protobuf:"varint,2,opt,name=type,proto3,enum=kibana.KibanaLog_PhoneType" json:"type,omitempty"`
}

func (x *KibanaLog_PhoneNumber) Reset() {
	*x = KibanaLog_PhoneNumber{}
	if protoimpl.UnsafeEnabled {
		mi := &file_KibanaLog_proto_msgTypes[2]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *KibanaLog_PhoneNumber) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*KibanaLog_PhoneNumber) ProtoMessage() {}

func (x *KibanaLog_PhoneNumber) ProtoReflect() protoreflect.Message {
	mi := &file_KibanaLog_proto_msgTypes[2]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use KibanaLog_PhoneNumber.ProtoReflect.Descriptor instead.
func (*KibanaLog_PhoneNumber) Descriptor() ([]byte, []int) {
	return file_KibanaLog_proto_rawDescGZIP(), []int{0, 0}
}

func (x *KibanaLog_PhoneNumber) GetNumber() string {
	if x != nil {
		return x.Number
	}
	return ""
}

func (x *KibanaLog_PhoneNumber) GetType() KibanaLog_PhoneType {
	if x != nil {
		return x.Type
	}
	return KibanaLog_MOBILE
}

var File_KibanaLog_proto protoreflect.FileDescriptor

var file_KibanaLog_proto_rawDesc = []byte{
	0x0a, 0x0f, 0x4b, 0x69, 0x62, 0x61, 0x6e, 0x61, 0x4c, 0x6f, 0x67, 0x2e, 0x70, 0x72, 0x6f, 0x74,
	0x6f, 0x12, 0x06, 0x6b, 0x69, 0x62, 0x61, 0x6e, 0x61, 0x22, 0x81, 0x02, 0x0a, 0x09, 0x4b, 0x69,
	0x62, 0x61, 0x6e, 0x61, 0x4c, 0x6f, 0x67, 0x12, 0x12, 0x0a, 0x04, 0x6e, 0x61, 0x6d, 0x65, 0x18,
	0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x04, 0x6e, 0x61, 0x6d, 0x65, 0x12, 0x0e, 0x0a, 0x02, 0x69,
	0x64, 0x18, 0x02, 0x20, 0x01, 0x28, 0x05, 0x52, 0x02, 0x69, 0x64, 0x12, 0x14, 0x0a, 0x05, 0x65,
	0x6d, 0x61, 0x69, 0x6c, 0x18, 0x03, 0x20, 0x01, 0x28, 0x09, 0x52, 0x05, 0x65, 0x6d, 0x61, 0x69,
	0x6c, 0x12, 0x35, 0x0a, 0x06, 0x70, 0x68, 0x6f, 0x6e, 0x65, 0x73, 0x18, 0x04, 0x20, 0x03, 0x28,
	0x0b, 0x32, 0x1d, 0x2e, 0x6b, 0x69, 0x62, 0x61, 0x6e, 0x61, 0x2e, 0x4b, 0x69, 0x62, 0x61, 0x6e,
	0x61, 0x4c, 0x6f, 0x67, 0x2e, 0x50, 0x68, 0x6f, 0x6e, 0x65, 0x4e, 0x75, 0x6d, 0x62, 0x65, 0x72,
	0x52, 0x06, 0x70, 0x68, 0x6f, 0x6e, 0x65, 0x73, 0x1a, 0x56, 0x0a, 0x0b, 0x50, 0x68, 0x6f, 0x6e,
	0x65, 0x4e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0x12, 0x16, 0x0a, 0x06, 0x6e, 0x75, 0x6d, 0x62, 0x65,
	0x72, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x06, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0x12,
	0x2f, 0x0a, 0x04, 0x74, 0x79, 0x70, 0x65, 0x18, 0x02, 0x20, 0x01, 0x28, 0x0e, 0x32, 0x1b, 0x2e,
	0x6b, 0x69, 0x62, 0x61, 0x6e, 0x61, 0x2e, 0x4b, 0x69, 0x62, 0x61, 0x6e, 0x61, 0x4c, 0x6f, 0x67,
	0x2e, 0x50, 0x68, 0x6f, 0x6e, 0x65, 0x54, 0x79, 0x70, 0x65, 0x52, 0x04, 0x74, 0x79, 0x70, 0x65,
	0x22, 0x2b, 0x0a, 0x09, 0x50, 0x68, 0x6f, 0x6e, 0x65, 0x54, 0x79, 0x70, 0x65, 0x12, 0x0a, 0x0a,
	0x06, 0x4d, 0x4f, 0x42, 0x49, 0x4c, 0x45, 0x10, 0x00, 0x12, 0x08, 0x0a, 0x04, 0x48, 0x4f, 0x4d,
	0x45, 0x10, 0x01, 0x12, 0x08, 0x0a, 0x04, 0x57, 0x4f, 0x52, 0x4b, 0x10, 0x02, 0x22, 0x38, 0x0a,
	0x0b, 0x41, 0x64, 0x64, 0x72, 0x65, 0x73, 0x73, 0x42, 0x6f, 0x6f, 0x6b, 0x12, 0x29, 0x0a, 0x06,
	0x70, 0x65, 0x6f, 0x70, 0x6c, 0x65, 0x18, 0x01, 0x20, 0x03, 0x28, 0x0b, 0x32, 0x11, 0x2e, 0x6b,
	0x69, 0x62, 0x61, 0x6e, 0x61, 0x2e, 0x4b, 0x69, 0x62, 0x61, 0x6e, 0x61, 0x4c, 0x6f, 0x67, 0x52,
	0x06, 0x70, 0x65, 0x6f, 0x70, 0x6c, 0x65, 0x42, 0x03, 0x5a, 0x01, 0x2e, 0x62, 0x06, 0x70, 0x72,
	0x6f, 0x74, 0x6f, 0x33,
}

var (
	file_KibanaLog_proto_rawDescOnce sync.Once
	file_KibanaLog_proto_rawDescData = file_KibanaLog_proto_rawDesc
)

func file_KibanaLog_proto_rawDescGZIP() []byte {
	file_KibanaLog_proto_rawDescOnce.Do(func() {
		file_KibanaLog_proto_rawDescData = protoimpl.X.CompressGZIP(file_KibanaLog_proto_rawDescData)
	})
	return file_KibanaLog_proto_rawDescData
}

var file_KibanaLog_proto_enumTypes = make([]protoimpl.EnumInfo, 1)
var file_KibanaLog_proto_msgTypes = make([]protoimpl.MessageInfo, 3)
var file_KibanaLog_proto_goTypes = []interface{}{
	(KibanaLog_PhoneType)(0),      // 0: kibana.KibanaLog.PhoneType
	(*KibanaLog)(nil),             // 1: kibana.KibanaLog
	(*AddressBook)(nil),           // 2: kibana.AddressBook
	(*KibanaLog_PhoneNumber)(nil), // 3: kibana.KibanaLog.PhoneNumber
}
var file_KibanaLog_proto_depIdxs = []int32{
	3, // 0: kibana.KibanaLog.phones:type_name -> kibana.KibanaLog.PhoneNumber
	1, // 1: kibana.AddressBook.people:type_name -> kibana.KibanaLog
	0, // 2: kibana.KibanaLog.PhoneNumber.type:type_name -> kibana.KibanaLog.PhoneType
	3, // [3:3] is the sub-list for method output_type
	3, // [3:3] is the sub-list for method input_type
	3, // [3:3] is the sub-list for extension type_name
	3, // [3:3] is the sub-list for extension extendee
	0, // [0:3] is the sub-list for field type_name
}

func init() { file_KibanaLog_proto_init() }
func file_KibanaLog_proto_init() {
	if File_KibanaLog_proto != nil {
		return
	}
	if !protoimpl.UnsafeEnabled {
		file_KibanaLog_proto_msgTypes[0].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*KibanaLog); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_KibanaLog_proto_msgTypes[1].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*AddressBook); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_KibanaLog_proto_msgTypes[2].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*KibanaLog_PhoneNumber); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_KibanaLog_proto_rawDesc,
			NumEnums:      1,
			NumMessages:   3,
			NumExtensions: 0,
			NumServices:   0,
		},
		GoTypes:           file_KibanaLog_proto_goTypes,
		DependencyIndexes: file_KibanaLog_proto_depIdxs,
		EnumInfos:         file_KibanaLog_proto_enumTypes,
		MessageInfos:      file_KibanaLog_proto_msgTypes,
	}.Build()
	File_KibanaLog_proto = out.File
	file_KibanaLog_proto_rawDesc = nil
	file_KibanaLog_proto_goTypes = nil
	file_KibanaLog_proto_depIdxs = nil
}